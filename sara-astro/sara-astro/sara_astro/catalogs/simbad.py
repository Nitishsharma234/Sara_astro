"""
Thin, typed wrapper around astroquery.simbad.Simbad.

This module handles SIMBAD I/O and converts the result into a
SimbadRecord that the rest of SARA Astro can use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sara_astro.exceptions import (
    CatalogConnectionError,
    ObjectNotFoundError,
)


# SIMBAD fields requested from astroquery.
_VOTABLE_FIELDS = [
    "ids",
    "otype",
    "sp",
    "plx",
    "plx_error",
    "flux(V)",
    "flux(B)",
    "flux(K)",
]


@dataclass
class SimbadRecord:
    """Data returned for one object from SIMBAD."""

    main_id: str
    ra_deg: float | None
    dec_deg: float | None

    object_type: str | None = None
    spectral_type: str | None = None

    parallax_mas: float | None = None
    parallax_error_mas: float | None = None

    v_mag: float | None = None
    b_mag: float | None = None
    k_mag: float | None = None

    all_ids: list[str] = field(default_factory=list)


def _get_simbad_client():
    """Create and configure a SIMBAD client."""

    from astroquery.simbad import Simbad

    simbad = Simbad()

    simbad.add_votable_fields(*_VOTABLE_FIELDS)

    simbad.TIMEOUT = 20

    return simbad


def _get_column(row: Any, *candidate_names: str) -> Any:
    """
    Return the first available value from the supplied column names.

    Different astroquery/SIMBAD versions may return slightly different
    column names, so multiple candidates can be supplied.
    """

    colnames = row.colnames if hasattr(row, "colnames") else []

    for name in candidate_names:

        if name not in colnames:
            continue

        value = row[name]

        try:
            if value is None:
                continue

            if hasattr(value, "mask") and value.mask:
                continue

        except (AttributeError, ValueError):
            pass

        return value

    return None


def _to_float(value: Any) -> float | None:
    """Safely convert a value to float."""

    if value is None:
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def _to_string(value: Any) -> str | None:
    """Safely convert a value to string."""

    if value is None:
        return None

    try:
        text = str(value).strip()

        if not text:
            return None

        return text

    except Exception:
        return None


def query_object(identifier: str) -> SimbadRecord:
    """
    Query SIMBAD for one astronomical object.

    Example:

        query_object("Sirius")
        query_object("HD 48915")
        query_object("* alf CMa")
    """

    try:

        simbad = _get_simbad_client()

        result = simbad.query_object(identifier)

    except ObjectNotFoundError:

        raise

    except Exception as exc:

        raise CatalogConnectionError(
            "SIMBAD",
            detail=str(exc),
        ) from exc

    if result is None or len(result) == 0:

        raise ObjectNotFoundError(identifier)

    row = result[0]

    # ---------------------------------------------------------
    # Basic fields
    # ---------------------------------------------------------

    main_id = _get_column(
        row,
        "MAIN_ID",
        "main_id",
    )

    ra = _get_column(
        row,
        "RA",
        "ra",
    )

    dec = _get_column(
        row,
        "DEC",
        "dec",
    )

    object_type = _get_column(
        row,
        "OTYPE",
        "otype",
    )

    # ---------------------------------------------------------
    # Spectral type
    # ---------------------------------------------------------
    #
    # Different SIMBAD/astroquery versions can expose this as
    # SP_TYPE, SP, or sp.
    #
    spectral_type = _get_column(
        row,
        "sp_type",
        "SP_TYPE",
        "SP",
        "sp",
    )
    # ---------------------------------------------------------
    # Parallax
    # ---------------------------------------------------------

    parallax = _get_column(
        row,
        "PLX_VALUE",
        "plx",
        "plx_value",
    )

    parallax_error = _get_column(
        row,
        "PLX_ERROR",
        "plx_error",
    )

    # ---------------------------------------------------------
    # Photometry
    # ---------------------------------------------------------

    v_mag = _get_column(
        row,
        "FLUX_V",
        "V",
        "flux(V)",
    )

    b_mag = _get_column(
        row,
        "FLUX_B",
        "B",
        "flux(B)",
    )

    k_mag = _get_column(
        row,
        "FLUX_K",
        "K",
        "flux(K)",
    )

    # ---------------------------------------------------------
    # Identifiers
    # ---------------------------------------------------------

    ids_raw = _get_column(
        row,
        "IDS",
        "ids",
    )

    all_ids: list[str] = []

    if ids_raw is not None:

        try:

            raw_string = str(ids_raw)

            all_ids = [
                item.strip()
                for item in raw_string.split("|")
                if item.strip()
            ]

        except Exception:
            all_ids = []

    # ---------------------------------------------------------
    # Coordinates
    # ---------------------------------------------------------

    ra_deg = _to_float(ra)
    dec_deg = _to_float(dec)

    # SIMBAD may return RA/DEC as sexagesimal strings.
    # If that happens, perform a second query requesting
    # decimal-degree coordinates.
    if ra_deg is None or dec_deg is None:

        ra_deg, dec_deg = _query_coordinates_deg(
            identifier
        )

    # ---------------------------------------------------------
    # Return typed record
    # ---------------------------------------------------------

    return SimbadRecord(
        main_id=(
            str(main_id)
            if main_id is not None
            else identifier
        ),

        ra_deg=ra_deg,
        dec_deg=dec_deg,

        object_type=_to_string(object_type),

        spectral_type=_to_string(spectral_type),

        parallax_mas=_to_float(parallax),

        parallax_error_mas=_to_float(
            parallax_error
        ),

        v_mag=_to_float(v_mag),

        b_mag=_to_float(b_mag),

        k_mag=_to_float(k_mag),

        all_ids=all_ids,
    )


def _query_coordinates_deg(
    identifier: str,
) -> tuple[float | None, float | None]:
    """
    Query SIMBAD specifically for decimal-degree coordinates.
    """

    try:

        from astroquery.simbad import Simbad

        simbad = Simbad()

        simbad.add_votable_fields(
            "ra(d)",
            "dec(d)",
        )

        result = simbad.query_object(
            identifier
        )

    except Exception:

        return None, None

    if result is None or len(result) == 0:

        return None, None

    row = result[0]

    ra = _get_column(
        row,
        "RA_d",
        "ra_d",
    )

    dec = _get_column(
        row,
        "DEC_d",
        "dec_d",
    )

    try:

        ra_value = (
            float(ra)
            if ra is not None
            else None
        )

        dec_value = (
            float(dec)
            if dec is not None
            else None
        )

        return ra_value, dec_value

    except (TypeError, ValueError):

        return None, None