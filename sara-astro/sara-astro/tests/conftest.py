"""Shared fixtures.

These fixtures build fake SIMBAD/Gaia records directly (bypassing the
network entirely) so the test suite runs fully offline and deterministically
in CI, while still exercising the exact same object/resolver/physics code
paths that a live catalog response would flow through.
"""

from __future__ import annotations

import pytest

from sara_astro.catalogs.simbad import SimbadRecord


@pytest.fixture
def sirius_simbad_record() -> SimbadRecord:
    """A SIMBAD record shaped like the real Sirius A entry (values are
    illustrative and taken from the well-known, published SIMBAD/Gaia
    figures for Sirius A, not invented)."""
    return SimbadRecord(
        main_id="* alf CMa",
        ra_deg=101.28715533,
        dec_deg=-16.71611586,
        object_type="SB*",
        spectral_type="A0m...",
        parallax_mas=379.21,
        parallax_error_mas=1.58,
        v_mag=-1.46,
        b_mag=-1.46,
        k_mag=-1.39,
        all_ids=[
            "* alf CMa",
            "HD 48915",
            "HIP 32349",
            "Gaia DR3 2947050466531873024",
            "TYC 5949-2777-1",
        ],
    )
