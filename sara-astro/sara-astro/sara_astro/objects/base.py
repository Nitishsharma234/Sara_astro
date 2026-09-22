"""AstroObject — the unified, SIMBAD-backed entry point.

This class resolves an astronomical identifier and retrieves
available information from SIMBAD.

Gaia is intentionally not used in the current MVP.
"""

from __future__ import annotations

import astropy.units as u

from sara_astro.catalogs import simbad
from sara_astro.identification.resolver import ResolvedIdentity, resolve
from sara_astro.utils import cache as cache_module
from sara_astro.utils.units import DataKind, DataValue


class AstroObject:
    """A unified view of one astronomical object backed by SIMBAD.

    Example:
        >>> obj = AstroObject("Sirius")  # doctest: +SKIP
        >>> obj.distance()               # doctest: +SKIP

    Args:
        identifier: A name or catalog identifier such as
            ``"Sirius"``, ``"HD 48915"``, or ``"HIP 32349"``.

        online: If True, query SIMBAD during construction.
            If False, no network calls are made.

        cache: If True, cache SIMBAD responses on disk.
    """

    _CACHE_NAMESPACE = "astro_object"

    def __init__(
        self,
        identifier: str,
        online: bool = True,
        cache: bool = False,
    ) -> None:

        self.identifier = identifier
        self._online = online
        self._cache = cache

        self._identity: ResolvedIdentity | None = None
        self._simbad_record = None

        if online:
            self._load(identifier)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _load(self, identifier: str) -> None:

        cache_key = identifier.strip().lower()

        # Try cache first
        if self._cache:

            cached = cache_module.get(
                self._CACHE_NAMESPACE,
                cache_key,
            )

            if cached is not None:

                self._identity = ResolvedIdentity(
                    **cached["identity"]
                )

                cached_simbad = cached.get("simbad")

                if cached_simbad is not None:
                    from sara_astro.catalogs.simbad import SimbadRecord

                    self._simbad_record = SimbadRecord(
                        **cached_simbad
                    )

                return

        # Resolve identifier
        self._identity = resolve(identifier)

        # Query SIMBAD
        self._simbad_record = simbad.query_object(identifier)

        # Save cache
        if self._cache:

            cache_module.set(
                self._CACHE_NAMESPACE,
                cache_key,
                {
                    "identity": vars(self._identity),
                    "simbad": (
                        vars(self._simbad_record)
                        if self._simbad_record
                        else None
                    ),
                },
            )

    @staticmethod
    def clear_cache() -> None:
        """Clear all cached AstroObject data."""

        cache_module.clear(
            AstroObject._CACHE_NAMESPACE
        )

    # ------------------------------------------------------------------
    # Identifiers
    # ------------------------------------------------------------------

    def identifiers(self) -> dict[str, str | None]:
        """Return known identifiers for this object."""

        if self._identity is None:
            return {
                "input": self.identifier
            }

        return {
            "input": self._identity.input_name,
            "simbad": self._identity.simbad_id,
            "hip": self._identity.hip_id,
            "hd": self._identity.hd_id,
            "tyc": self._identity.tyc_id,
            "gaia_dr3": self._identity.gaia_dr3_id,
            "object_type": self._identity.object_type,
        }

    # ------------------------------------------------------------------
    # Position
    # ------------------------------------------------------------------

    def position(self) -> dict[str, DataValue]:
        """Return right ascension and declination."""

        if (
            self._simbad_record is None
            or self._simbad_record.ra_deg is None
        ):

            unavailable = DataValue.unavailable(
                source="SIMBAD"
            )

            return {
                "ra": unavailable,
                "dec": unavailable,
            }

        return {
            "ra": DataValue(
                value=self._simbad_record.ra_deg,
                unit=u.deg,
                kind=DataKind.OBSERVED,
                source="SIMBAD",
            ),

            "dec": DataValue(
                value=self._simbad_record.dec_deg,
                unit=u.deg,
                kind=DataKind.OBSERVED,
                source="SIMBAD",
            ),
        }

    # ------------------------------------------------------------------
    # Distance
    # ------------------------------------------------------------------

    def distance(self) -> DataValue:
        """Return distance derived from SIMBAD parallax.

        Uses:

            d = 1000 / parallax_mas

        to obtain distance in parsecs.
        """

        if (
            self._simbad_record is None
            or self._simbad_record.parallax_mas is None
        ):

            return DataValue.unavailable(
                source="SIMBAD"
            )

        plx_mas = self._simbad_record.parallax_mas
        plx_err_mas = self._simbad_record.parallax_error_mas

        if plx_mas <= 0:

            return DataValue.unavailable(
                source="SIMBAD"
            )

        distance_pc = 1000.0 / plx_mas

        uncertainty_pc = None

        if plx_err_mas:

            uncertainty_pc = (
                distance_pc
                * (plx_err_mas / plx_mas)
            )

        return DataValue(
            value=distance_pc,
            unit=u.pc,
            kind=DataKind.DERIVED,
            source=(
                "derived from SIMBAD parallax "
                "(d = 1000/plx_mas)"
            ),
            uncertainty=uncertainty_pc,
        )

    # ------------------------------------------------------------------
    # Photometry
    # ------------------------------------------------------------------

    def photometry(self) -> dict[str, DataValue]:
        """Return available V, B and K magnitudes."""

        if self._simbad_record is None:

            unavailable = DataValue.unavailable(
                source="SIMBAD"
            )

            return {
                "V": unavailable,
                "B": unavailable,
                "K": unavailable,
            }

        def mag(value: float | None) -> DataValue:

            if value is None:

                return DataValue.unavailable(
                    source="SIMBAD"
                )

            return DataValue(
                value=value,
                unit=u.mag,
                kind=DataKind.OBSERVED,
                source="SIMBAD",
            )

        return {
            "V": mag(self._simbad_record.v_mag),
            "B": mag(self._simbad_record.b_mag),
            "K": mag(self._simbad_record.k_mag),
        }

    # ------------------------------------------------------------------
    # Physical properties
    # ------------------------------------------------------------------

    def physical_properties(
        self,
    ) -> dict[str, DataValue]:
        """Return physical properties currently available.

        Currently this includes spectral type from SIMBAD.

        Temperature, radius and mass are not fetched automatically
        in the current MVP.
        """

        result: dict[str, DataValue] = {}

        if (
            self._simbad_record
            and self._simbad_record.spectral_type
        ):

            result["spectral_type"] = DataValue(
                value=self._simbad_record.spectral_type,
                unit=None,
                kind=DataKind.OBSERVED,
                source="SIMBAD",
            )

        else:

            result["spectral_type"] = (
                DataValue.unavailable(
                    source="SIMBAD"
                )
            )

        # Gaia is intentionally not used currently.
        result["temperature"] = DataValue.unavailable(
            source="SIMBAD"
        )

        result["radius"] = DataValue.unavailable(
            source="SIMBAD"
        )

        return result

    # ------------------------------------------------------------------
    # Spectral information
    # ------------------------------------------------------------------

    def spectral_information(self) -> DataValue:
        """Return the spectral type."""

        return self.physical_properties()[
            "spectral_type"
        ]

    # ------------------------------------------------------------------
    # Available data
    # ------------------------------------------------------------------

    def available_data(self) -> dict[str, bool]:
        """Report which data categories are available."""

        return {
            "identifiers": self._identity is not None,

            "position": (
                self.position()["ra"].is_available
            ),

            "distance": (
                self.distance().is_available
            ),

            "photometry": any(
                value.is_available
                for value in self.photometry().values()
            ),

            "physical_properties": any(
                value.is_available
                for value in self.physical_properties().values()
            ),
        }

    # ------------------------------------------------------------------
    # Human-readable information
    # ------------------------------------------------------------------

    def info(self) -> str:
        """Return a beginner-friendly summary."""

        ids = self.identifiers()
        pos = self.position()
        dist = self.distance()
        props = self.physical_properties()

        lines = [
            f"Object: "
            f"{ids.get('simbad') or self.identifier}",
            "",
        ]

        lines.append("Identifiers:")

        for label, key in (
            ("SIMBAD", "simbad"),
            ("HIP", "hip"),
            ("HD", "hd"),
            ("TYC", "tyc"),
        ):

            lines.append(
                f"  {label}: "
                f"{ids.get(key) or 'Not available'}"
            )

        lines.append("")

        lines.append("Position:")

        lines.append(
            f"  RA:  {pos['ra']}"
        )

        lines.append(
            f"  DEC: {pos['dec']}"
        )

        lines.append("")

        lines.append("Distance:")

        lines.append(
            f"  {dist}"
        )

        lines.append("")

        lines.append("Photometry:")

        photometry = self.photometry()

        lines.append(
            f"  V: {photometry['V']}"
        )

        lines.append(
            f"  B: {photometry['B']}"
        )

        lines.append(
            f"  K: {photometry['K']}"
        )

        lines.append("")

        lines.append("Physical properties:")

        lines.append(
            f"  Temperature: "
            f"{props['temperature']}"
        )

        lines.append(
            f"  Radius: "
            f"{props['radius']}"
        )

        lines.append("")

        lines.append(
            f"Spectral type: "
            f"{props['spectral_type']}"
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        simbad_id = (
            self._identity.simbad_id
            if self._identity
            else self.identifier
        )

        return f"AstroObject({simbad_id!r})"