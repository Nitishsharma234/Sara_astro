from __future__ import annotations

import astropy.units as u
import pytest

from sara_astro.exceptions import ObjectNotFoundError
from sara_astro.identification.resolver import ResolvedIdentity
from sara_astro.objects.base import AstroObject


@pytest.fixture
def mocked_sirius(mocker, sirius_simbad_record):

    identity = ResolvedIdentity(
        input_name="Sirius",
        simbad_id="* alf CMa",
        object_type="SB*",
        hip_id="32349",
        hd_id="48915",
        gaia_dr3_id="2947050466531873024",
        all_ids=sirius_simbad_record.all_ids,
    )

    mocker.patch(
        "sara_astro.objects.base.resolve",
        return_value=identity,
    )

    mocker.patch(
        "sara_astro.objects.base.simbad.query_object",
        return_value=sirius_simbad_record,
    )

    return AstroObject("Sirius")


def test_identifiers(mocked_sirius):

    ids = mocked_sirius.identifiers()

    assert ids["simbad"] == "* alf CMa"
    assert ids["hip"] == "32349"
    assert ids["hd"] == "48915"


def test_position_is_observed(mocked_sirius):

    pos = mocked_sirius.position()

    assert pos["ra"].is_available
    assert pos["ra"].unit == u.deg
    assert pos["ra"].kind.value == "observed"

    assert pos["dec"].is_available
    assert pos["dec"].unit == u.deg
    assert pos["dec"].kind.value == "observed"


def test_distance_is_derived_from_simbad_parallax(
    mocked_sirius,
):

    dist = mocked_sirius.distance()

    assert dist.is_available
    assert dist.unit == u.pc

    assert dist.value == pytest.approx(
        1000.0 / 379.21
    )

    assert "SIMBAD" in dist.source


def test_physical_properties_use_simbad(
    mocked_sirius,
):

    props = mocked_sirius.physical_properties()

    assert props["spectral_type"].is_available
    assert props["spectral_type"].kind.value == "observed"
    assert props["spectral_type"].source == "SIMBAD"


def test_temperature_is_unavailable_without_gaia(
    mocked_sirius,
):

    props = mocked_sirius.physical_properties()

    assert props["temperature"].is_available is False


def test_radius_is_unavailable_without_gaia(
    mocked_sirius,
):

    props = mocked_sirius.physical_properties()

    assert props["radius"].is_available is False


def test_available_data_reports_true_for_known_fields(
    mocked_sirius,
):

    avail = mocked_sirius.available_data()

    assert avail["identifiers"] is True
    assert avail["position"] is True
    assert avail["distance"] is True
    assert avail["photometry"] is True
    assert avail["physical_properties"] is True


def test_info_produces_readable_summary(
    mocked_sirius,
):

    text = mocked_sirius.info()

    assert "Object:" in text
    assert "Identifiers:" in text
    assert "Position:" in text
    assert "Distance:" in text
    assert "Photometry:" in text
    assert "Physical properties:" in text


def test_object_not_found_propagates(mocker):

    mocker.patch(
        "sara_astro.objects.base.resolve",
        side_effect=ObjectNotFoundError(
            "nonexistent-xyz"
        ),
    )

    with pytest.raises(ObjectNotFoundError):
        AstroObject("nonexistent-xyz")


def test_missing_parallax_gives_unavailable_distance(
    mocker,
    sirius_simbad_record,
):

    sirius_simbad_record.parallax_mas = None

    identity = ResolvedIdentity(
        input_name="Sirius",
        simbad_id="* alf CMa",
        object_type="SB*",
        all_ids=[],
    )

    mocker.patch(
        "sara_astro.objects.base.resolve",
        return_value=identity,
    )

    mocker.patch(
        "sara_astro.objects.base.simbad.query_object",
        return_value=sirius_simbad_record,
    )

    obj = AstroObject("Sirius")

    assert obj.distance().is_available is False