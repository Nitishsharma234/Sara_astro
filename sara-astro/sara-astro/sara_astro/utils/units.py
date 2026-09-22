"""The provenance data model at the heart of SARA Astro.

Every scientific quantity returned by this library — a mass, a distance,
a temperature — is wrapped in a :class:`DataValue` rather than returned as
a bare number. This is a deliberate, non-negotiable design choice: a number
without knowing whether it was *observed*, *derived*, or *estimated*, and
without knowing its source, is scientifically meaningless in an astronomy
context where the same "mass of Sirius" can differ across catalogs and
estimation methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import astropy.units as u


class DataKind(str, Enum):
    """Classifies how a :class:`DataValue` was obtained."""

    OBSERVED = "observed"    # Directly read from a catalog/observation.
    DERIVED = "derived"      # Calculated from other observed values via a documented equation.
    ESTIMATED = "estimated"  # Produced by a model, fit, or approximation method.
    UNAVAILABLE = "unavailable"  # Not currently obtainable for this object.


@dataclass(frozen=True)
class DataValue:
    """A scientific value carrying full provenance.

    Attributes:
        value: The numeric or string value, or ``None`` if unavailable.
        unit: An ``astropy.units.Unit`` (or ``None`` for dimensionless /
            unavailable / string values such as a spectral type).
        kind: One of :class:`DataKind` — how this value was obtained.
        source: Short human-readable source, e.g. ``"SIMBAD"``,
            ``"Gaia DR3"``, or ``"derived: L = 4*pi*R^2*sigma*T^4"``.
        original_identifier: The identifier used to look this value up in
            its source catalog, if applicable (e.g. the Gaia source_id used
            to pull a parallax).
        uncertainty: The +/- uncertainty on ``value``, in the same unit,
            if the source catalog reports one.
    """

    value: Any = None
    unit: u.UnitBase | None = None
    kind: DataKind = DataKind.UNAVAILABLE
    source: str | None = None
    original_identifier: str | None = None
    uncertainty: float | None = None

    @classmethod
    def unavailable(cls, source: str | None = None) -> DataValue:
        """Convenience constructor for a missing value.

        Use this instead of returning ``None`` directly so callers always
        get a consistent, introspectable object back.
        """
        return cls(value=None, kind=DataKind.UNAVAILABLE, source=source)

    @property
    def is_available(self) -> bool:
        return self.kind != DataKind.UNAVAILABLE and self.value is not None

    def to(self, new_unit: u.UnitBase) -> DataValue:
        """Return a copy converted to ``new_unit``, preserving provenance.

        Raises:
            sara_astro.exceptions.InvalidParameterError: if this value has
                no unit, is unavailable, or the unit is not convertible.
        """
        from sara_astro.exceptions import InvalidParameterError

        if not self.is_available:
            raise InvalidParameterError("Cannot convert an unavailable DataValue.")
        if self.unit is None:
            raise InvalidParameterError("This DataValue has no unit to convert from.")
        try:
            quantity = (self.value * self.unit).to(new_unit)
        except u.UnitConversionError as exc:
            raise InvalidParameterError(
                f"Cannot convert {self.unit} to {new_unit}: {exc}"
            ) from exc
        new_uncertainty = None
        if self.uncertainty is not None:
            new_uncertainty = (self.uncertainty * self.unit).to(new_unit).value
        return DataValue(
            value=quantity.value,
            unit=new_unit,
            kind=self.kind,
            source=self.source,
            original_identifier=self.original_identifier,
            uncertainty=new_uncertainty,
        )

    def __str__(self) -> str:
        if not self.is_available:
            src = f" (source: {self.source})" if self.source else ""
            return f"Not available{src}"
        unit_str = f" {self.unit}" if self.unit is not None else ""
        unc_str = f" ± {self.uncertainty}{unit_str}" if self.uncertainty is not None else ""
        src_str = f" [{self.kind.value}, source: {self.source}]" if self.source else f" [{self.kind.value}]"
        return f"{self.value}{unit_str}{unc_str}{src_str}"

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"DataValue(value={self.value!r}, unit={self.unit!r}, "
            f"kind={self.kind.value!r}, source={self.source!r}, "
            f"uncertainty={self.uncertainty!r})"
        )
