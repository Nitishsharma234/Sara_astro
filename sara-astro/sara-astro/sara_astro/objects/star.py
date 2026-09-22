"""``Star`` — catalog-backed or fully offline stellar object.

Two distinct usage modes, matching the project spec:

    Star("Sirius")                                    # online, catalog-backed
    Star(mass=2.0, radius=1.7, temperature=9900)       # offline, manual params

Offline mode never touches the network — it is a pure calculator over the
parameters you supply. Any calculation that needs a parameter you did not
supply returns ``DataValue.unavailable()`` rather than guessing.
"""

from __future__ import annotations

import math

import astropy.units as u
from astropy.constants import G, sigma_sb

from sara_astro.exceptions import InvalidParameterError
from sara_astro.objects.base import AstroObject
from sara_astro.utils.units import DataKind, DataValue
from sara_astro.utils.validation import require_positive


class Star(AstroObject):
    """A star, either resolved from catalogs or fully specified offline.

    Args:
        identifier: Catalog name/ID for online mode (e.g. ``"Sirius"``).
            Mutually exclusive with the offline keyword parameters below.
        mass: Mass in solar masses, for offline mode.
        radius: Radius in solar radii, for offline mode.
        temperature: Effective temperature in Kelvin, for offline mode.
        online: See :class:`~sara_astro.objects.base.AstroObject`. Ignored
            in offline mode.
        cache: See :class:`~sara_astro.objects.base.AstroObject`. Ignored
            in offline mode.

    Raises:
        sara_astro.exceptions.InvalidParameterError: if neither an
            ``identifier`` nor at least one offline parameter is given, or
            if a supplied offline parameter is not a finite positive
            number.
    """

    def __init__(
        self,
        identifier: str | None = None,
        *,
        mass: float | None = None,
        radius: float | None = None,
        temperature: float | None = None,
        online: bool = True,
        cache: bool = False,
    ) -> None:
        self._offline_mode = identifier is None

        if self._offline_mode:
            if mass is None and radius is None and temperature is None:
                raise InvalidParameterError(
                    "Star requires either an identifier (online mode) or at "
                    "least one of mass/radius/temperature (offline mode)."
                )
            self._mass_msun = require_positive(mass, "mass") if mass is not None else None
            self._radius_rsun = require_positive(radius, "radius") if radius is not None else None
            self._temperature_k = (
                require_positive(temperature, "temperature") if temperature is not None else None
            )
            self.identifier = "offline star"
            self._identity = None
            self._simbad_record = None
            self._gaia_record = None
            self._online = False
            self._cache = False
        else:
            super().__init__(identifier, online=online, cache=cache)
            self._mass_msun = None
            self._radius_rsun = None
            self._temperature_k = None
            if not self._offline_mode:
                props = self.physical_properties()
                if props["radius"].is_available:
                    self._radius_rsun = props["radius"].value
                if props["temperature"].is_available:
                    self._temperature_k = props["temperature"].value

    # -- stellar physics ----------------------------------------------------

    def surface_gravity(self) -> DataValue:
        """Surface gravity ``g = G*M/R^2``.

        Requires mass and radius. In online mode, mass is rarely available
        directly from SIMBAD/Gaia for typical stars (it usually requires a
        binary orbit or an asteroseismic/evolutionary model), so this will
        commonly be unavailable unless you're in offline mode with mass
        supplied, or a future catalog module supplies it.
        """
        if self._mass_msun is None or self._radius_rsun is None:
            return DataValue.unavailable(
                source="derived: g = G*M/R^2 (requires mass and radius)"
            )
        mass = self._mass_msun * u.M_sun
        radius = self._radius_rsun * u.R_sun
        g = (G * mass / radius**2).to(u.m / u.s**2)
        return DataValue(
            value=g.value,
            unit=u.m / u.s**2,
            kind=DataKind.DERIVED,
            source="derived: g = G*M/R^2",
        )

    def density(self) -> DataValue:
        """Mean density ``rho = M / (4/3 * pi * R^3)``."""
        if self._mass_msun is None or self._radius_rsun is None:
            return DataValue.unavailable(
                source="derived: rho = M/((4/3)*pi*R^3) (requires mass and radius)"
            )
        mass = self._mass_msun * u.M_sun
        radius = self._radius_rsun * u.R_sun
        volume = (4.0 / 3.0) * math.pi * radius**3
        rho = (mass / volume).to(u.kg / u.m**3)
        return DataValue(
            value=rho.value,
            unit=u.kg / u.m**3,
            kind=DataKind.DERIVED,
            source="derived: rho = M/((4/3)*pi*R^3)",
        )

    def escape_velocity(self) -> DataValue:
        """Escape velocity ``v = sqrt(2*G*M/R)``."""
        if self._mass_msun is None or self._radius_rsun is None:
            return DataValue.unavailable(
                source="derived: v_esc = sqrt(2*G*M/R) (requires mass and radius)"
            )
        mass = self._mass_msun * u.M_sun
        radius = self._radius_rsun * u.R_sun
        v_esc = ((2 * G * mass / radius) ** 0.5).to(u.km / u.s)
        return DataValue(
            value=v_esc.value,
            unit=u.km / u.s,
            kind=DataKind.DERIVED,
            source="derived: v_esc = sqrt(2*G*M/R)",
        )

    def luminosity(self) -> DataValue:
        """Luminosity from the Stefan-Boltzmann law: ``L = 4*pi*R^2*sigma*T^4``.

        Requires radius and temperature (not mass) — this is the one
        stellar quantity that's realistically computable in online mode
        today, since Gaia's GSP-Phot pipeline provides both.
        """
        if self._radius_rsun is None or self._temperature_k is None:
            return DataValue.unavailable(
                source="derived: L = 4*pi*R^2*sigma*T^4 (requires radius and temperature)"
            )
        radius = self._radius_rsun * u.R_sun
        temperature = self._temperature_k * u.K
        luminosity = (4 * math.pi * radius**2 * sigma_sb * temperature**4).to(u.L_sun)
        return DataValue(
            value=luminosity.value,
            unit=u.L_sun,
            kind=DataKind.DERIVED,
            source="derived: L = 4*pi*R^2*sigma*T^4 (Stefan-Boltzmann law)",
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        if self._offline_mode:
            return (
                f"Star(mass={self._mass_msun}, radius={self._radius_rsun}, "
                f"temperature={self._temperature_k})"
            )
        return super().__repr__()
