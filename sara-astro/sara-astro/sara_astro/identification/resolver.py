"""Resolves a user-supplied name/identifier to a canonical identifier set.

This is the single place in the library that answers "what does SIMBAD
call this, and what does it also go by (HIP/HD/Gaia/...)?" No other module
re-implements name resolution — ``objects.base.AstroObject`` calls this
once and then asks the catalog adapters for further data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sara_astro.catalogs import simbad
from sara_astro.catalogs.gaia import extract_gaia_source_id
from sara_astro.utils.validation import sanitize_identifier

_PREFIX_MAP = {
    "HIP": "hip_id",
    "HD": "hd_id",
    "TYC": "tyc_id",
    "2MASS": "twomass_id",
}


@dataclass
class ResolvedIdentity:
    """The canonical identifier set for one astronomical object.

    Any field is ``None`` if that catalog does not list an identifier of
    that type for this object — SIMBAD not having, say, an HD number for a
    faint star is normal and expected, not an error.
    """

    input_name: str
    simbad_id: str
    object_type: str | None
    hip_id: str | None = None
    hd_id: str | None = None
    tyc_id: str | None = None
    twomass_id: str | None = None
    gaia_dr3_id: str | None = None
    all_ids: list[str] = field(default_factory=list)


def resolve(identifier: str) -> ResolvedIdentity:
    """Resolve ``identifier`` to a canonical, cross-referenced identity.

    Args:
        identifier: Any name or catalog ID a user might type, e.g.
            ``"Sirius"``, ``"HD 48915"``, ``"HIP 32349"``.

    Returns:
        A populated :class:`ResolvedIdentity`.

    Raises:
        sara_astro.exceptions.InvalidParameterError: if ``identifier`` is
            malformed (empty, absurdly long, invalid characters).
        sara_astro.exceptions.ObjectNotFoundError: if no known resolver
            recognizes ``identifier``.
        sara_astro.exceptions.CatalogConnectionError: if the resolver
            service could not be reached.
    """
    clean = sanitize_identifier(identifier)
    record = simbad.query_object(clean)

    identity = ResolvedIdentity(
        input_name=identifier,
        simbad_id=record.main_id,
        object_type=record.object_type,
        all_ids=record.all_ids,
        gaia_dr3_id=extract_gaia_source_id(record.all_ids),
    )

    for full_id in record.all_ids:
        for prefix, attr_name in _PREFIX_MAP.items():
            if full_id.startswith((prefix + " ", prefix)):
                value = full_id[len(prefix):].strip()
                if value and getattr(identity, attr_name) is None:
                    setattr(identity, attr_name, value)

    return identity
