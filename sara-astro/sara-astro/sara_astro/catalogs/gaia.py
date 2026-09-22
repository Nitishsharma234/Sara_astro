"""Best-effort Gaia DR3 cross-match wrapper.

Gaia can be queried either by an already-known Gaia source_id or by
sky position (RA/DEC).

Position-based lookup is used as a fallback when SIMBAD does not
provide a Gaia DR3 source_id.

All Gaia queries fail softly:
if Gaia is unavailable or a query fails, the function returns None.
"""

from __future__ import annotations

from dataclasses import dataclass

import astropy.units as u
from astropy.coordinates import SkyCoord


@dataclass
class GaiaRecord:
    """A subset of Gaia DR3 fields for one source."""

    source_id: str
    parallax_mas: float | None = None
    parallax_error_mas: float | None = None
    phot_g_mean_mag: float | None = None
    teff_gspphot: float | None = None
    radius_gspphot: float | None = None


def _value(row, name: str) -> float | None:
    """Safely extract a numeric value from a Gaia row."""

    try:
        value = row[name]

        if value is None:
            return None

        if hasattr(value, "mask") and value.mask:
            return None

        return float(value)

    except (KeyError, TypeError, ValueError):
        return None


def _record_from_row(row) -> GaiaRecord:
    """Convert one Gaia table row into a GaiaRecord."""

    return GaiaRecord(
        source_id=str(row["source_id"]),
        parallax_mas=_value(row, "parallax"),
        parallax_error_mas=_value(row, "parallax_error"),
        phot_g_mean_mag=_value(row, "phot_g_mean_mag"),
        teff_gspphot=_value(row, "teff_gspphot"),
        radius_gspphot=_value(row, "radius_gspphot"),
    )


def query_by_source_id(gaia_source_id: str) -> GaiaRecord | None:
    """Look up a Gaia DR3 record by source_id."""

    try:
        from astroquery.gaia import Gaia

        query = (
            "SELECT source_id, parallax, parallax_error, "
            "phot_g_mean_mag, teff_gspphot, radius_gspphot "
            "FROM gaiadr3.gaia_source "
            f"WHERE source_id = {int(gaia_source_id)}"
        )

        job = Gaia.launch_job(query)
        table = job.get_results()

    except Exception:
        return None

    if table is None or len(table) == 0:
        return None

    return _record_from_row(table[0])


def query_by_position(
    ra_deg: float,
    dec_deg: float,
    radius_arcsec: float = 2.0,
) -> GaiaRecord | None:
    """Find the nearest Gaia DR3 source around an RA/DEC position."""

    try:
        from astroquery.gaia import Gaia

        radius_deg = radius_arcsec / 3600.0

        query = f"""
        SELECT TOP 10
            source_id,
            ra,
            dec,
            parallax,
            parallax_error,
            phot_g_mean_mag,
            teff_gspphot

        FROM gaiadr3.gaia_source

        WHERE 1 = CONTAINS(
            POINT('ICRS', ra, dec),
            CIRCLE(
                'ICRS',
                {ra_deg},
                {dec_deg},
                {radius_deg}
            )
        )
        """

        print("Sending Gaia ADQL query...")

        job = Gaia.launch_job(query)

        print("Gaia query completed.")

        table = job.get_results()

    except Exception as e:
        print("Gaia query failed:", e)
        return None

    if table is None or len(table) == 0:
        print("No Gaia source found.")
        return None

    coordinate = SkyCoord(
        ra=ra_deg,
        dec=dec_deg,
        unit=(u.deg, u.deg),
        frame="icrs",
    )

    distances = []

    for row in table:

        source_coordinate = SkyCoord(
            ra=float(row["ra"]),
            dec=float(row["dec"]),
            unit=(u.deg, u.deg),
            frame="icrs",
        )

        distance = coordinate.separation(
            source_coordinate
        ).arcsec

        distances.append(distance)

    nearest_index = distances.index(min(distances))

    nearest_row = table[nearest_index]

    return GaiaRecord(
        source_id=str(nearest_row["source_id"]),
        parallax_mas=_value(nearest_row, "parallax"),
        parallax_error_mas=_value(
            nearest_row,
            "parallax_error",
        ),
        phot_g_mean_mag=_value(
            nearest_row,
            "phot_g_mean_mag",
        ),
        teff_gspphot=_value(
            nearest_row,
            "teff_gspphot",
        ),
        radius_gspphot=None,
    )

def extract_gaia_source_id(
    simbad_ids: list[str],
) -> str | None:
    """Pull a Gaia DR3 source_id from SIMBAD cross-identifiers."""

    for identifier in simbad_ids:

        if identifier.startswith("Gaia DR3 "):
            return identifier.removeprefix("Gaia DR3 ").strip()

    return None