from __future__ import annotations

import pytest

from sara_astro.exceptions import InvalidParameterError
from sara_astro.objects.star import Star


def test_offline_star_requires_at_least_one_param():
    with pytest.raises(InvalidParameterError):
        Star()


def test_offline_star_rejects_negative_mass():
    with pytest.raises(InvalidParameterError):
        Star(mass=-1.0)


def test_sun_like_star_surface_gravity_matches_known_value():
    # Using the Sun's own parameters should reproduce the Sun's known
    # surface gravity, log(g) ~= 4.44 (g ~= 274 m/s^2), within the
    # precision of solar mass/radius constants used.
    sun = Star(mass=1.0, radius=1.0, temperature=5772.0)
    g = sun.surface_gravity()
    assert g.is_available
    assert g.value == pytest.approx(274.0, rel=0.02)


def test_sun_luminosity_is_approximately_one_solar_luminosity():
    sun = Star(mass=1.0, radius=1.0, temperature=5772.0)
    lum = sun.luminosity()
    assert lum.is_available
    assert lum.value == pytest.approx(1.0, rel=0.05)


def test_escape_velocity_requires_mass_and_radius():
    star = Star(temperature=9900.0)  # no mass or radius supplied
    v_esc = star.escape_velocity()
    assert v_esc.is_available is False


def test_density_calculation():
    sun = Star(mass=1.0, radius=1.0, temperature=5772.0)
    rho = sun.density()
    # The Sun's known mean density is ~1408 kg/m^3.
    assert rho.value == pytest.approx(1408.0, rel=0.02)


def test_luminosity_missing_temperature_is_unavailable():
    star = Star(mass=1.0, radius=1.0)
    assert star.luminosity().is_available is False
