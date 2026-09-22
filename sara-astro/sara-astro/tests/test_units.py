from __future__ import annotations

import astropy.units as u
import pytest

from sara_astro.exceptions import InvalidParameterError
from sara_astro.utils.units import DataKind, DataValue


def test_unavailable_is_not_available():
    dv = DataValue.unavailable(source="SIMBAD")
    assert dv.is_available is False
    assert dv.kind == DataKind.UNAVAILABLE
    assert "Not available" in str(dv)


def test_observed_value_is_available():
    dv = DataValue(value=1.0, unit=u.pc, kind=DataKind.OBSERVED, source="Gaia")
    assert dv.is_available is True
    assert "pc" in str(dv)
    assert "observed" in str(dv)


def test_unit_conversion_preserves_provenance():
    dv = DataValue(value=1.0, unit=u.pc, kind=DataKind.DERIVED, source="derived", uncertainty=0.1)
    converted = dv.to(u.lyr)
    assert converted.kind == DataKind.DERIVED
    assert converted.source == "derived"
    assert converted.unit == u.lyr
    assert converted.value == pytest.approx((1.0 * u.pc).to(u.lyr).value)
    assert converted.uncertainty == pytest.approx((0.1 * u.pc).to(u.lyr).value)


def test_convert_unavailable_raises():
    dv = DataValue.unavailable()
    with pytest.raises(InvalidParameterError):
        dv.to(u.pc)


def test_convert_incompatible_unit_raises():
    dv = DataValue(value=1.0, unit=u.pc, kind=DataKind.OBSERVED, source="Gaia")
    with pytest.raises(InvalidParameterError):
        dv.to(u.kg)
