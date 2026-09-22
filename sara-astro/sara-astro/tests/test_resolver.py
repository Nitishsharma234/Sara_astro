from __future__ import annotations

import pytest

from sara_astro.exceptions import InvalidParameterError, ObjectNotFoundError
from sara_astro.identification import resolver


def test_resolve_extracts_cross_identifiers(mocker, sirius_simbad_record):
    mocker.patch(
        "sara_astro.identification.resolver.simbad.query_object",
        return_value=sirius_simbad_record,
    )

    identity = resolver.resolve("Sirius")

    assert identity.simbad_id == "* alf CMa"
    assert identity.hd_id == "48915"
    assert identity.hip_id == "32349"
    assert identity.gaia_dr3_id == "2947050466531873024"
    assert identity.object_type == "SB*"


def test_resolve_propagates_not_found(mocker):
    mocker.patch(
        "sara_astro.identification.resolver.simbad.query_object",
        side_effect=ObjectNotFoundError("not a real star"),
    )
    with pytest.raises(ObjectNotFoundError):
        resolver.resolve("not a real star")


def test_resolve_rejects_invalid_identifier_before_querying(mocker):
    spy = mocker.patch("sara_astro.identification.resolver.simbad.query_object")
    with pytest.raises(InvalidParameterError):
        resolver.resolve("")
    spy.assert_not_called()


def test_resolve_handles_missing_cross_ids_gracefully(mocker):
    from sara_astro.catalogs.simbad import SimbadRecord

    sparse_record = SimbadRecord(
        main_id="Some Faint Star",
        ra_deg=10.0,
        dec_deg=20.0,
        object_type="Star",
        all_ids=["Some Faint Star"],  # no HIP/HD/Gaia entries
    )
    mocker.patch(
        "sara_astro.identification.resolver.simbad.query_object",
        return_value=sparse_record,
    )

    identity = resolver.resolve("Some Faint Star")

    assert identity.hip_id is None
    assert identity.hd_id is None
    assert identity.gaia_dr3_id is None
