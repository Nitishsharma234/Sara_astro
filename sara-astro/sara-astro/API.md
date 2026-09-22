# API Reference (Phase 1)

## `sara_astro.AstroObject`

```python
AstroObject(identifier: str, online: bool = True, cache: bool = False)
```

| Method | Returns | Notes |
|---|---|---|
| `.identifiers()` | `dict[str, str \| None]` | SIMBAD/HIP/HD/Gaia DR3 IDs + object type |
| `.position()` | `dict[str, DataValue]` | `{"ra": ..., "dec": ...}` in degrees |
| `.distance()` | `DataValue` | Parsecs, derived from parallax (Gaia preferred, SIMBAD fallback) |
| `.photometry()` | `dict[str, DataValue]` | `{"V": ..., "B": ..., "K": ...}` magnitudes |
| `.physical_properties()` | `dict[str, DataValue]` | `spectral_type`, `temperature`, `radius` |
| `.spectral_information()` | `DataValue` | Spectral type only (full spectrum analysis: Phase 2) |
| `.available_data()` | `dict[str, bool]` | Which categories returned real data |
| `.info()` | `str` | Human-readable multi-line summary |
| `AstroObject.clear_cache()` | `None` | Static method — clears the on-disk cache |

## `sara_astro.Star` (extends `AstroObject`)

Online mode: `Star("Sirius")` — same methods as `AstroObject`, plus physics below.

Offline mode: `Star(mass=<Msun>, radius=<Rsun>, temperature=<K>)` — no network call.

| Method | Equation | Requires |
|---|---|---|
| `.surface_gravity()` | `g = G*M/R^2` | mass, radius |
| `.density()` | `rho = M/((4/3)*pi*R^3)` | mass, radius |
| `.escape_velocity()` | `v = sqrt(2*G*M/R)` | mass, radius |
| `.luminosity()` | `L = 4*pi*R^2*sigma*T^4` | radius, temperature |

Every method returns a `DataValue`; if a required input is missing, it
returns `DataValue.unavailable(...)` rather than raising.

## `sara_astro.utils.units.DataValue`

```python
@dataclass(frozen=True)
class DataValue:
    value: Any = None
    unit: astropy.units.UnitBase | None = None
    kind: DataKind = DataKind.UNAVAILABLE
    source: str | None = None
    original_identifier: str | None = None
    uncertainty: float | None = None
```

- `.is_available` — `bool`
- `.to(new_unit)` — unit-converted copy, provenance preserved
- `DataValue.unavailable(source=None)` — constructor for a missing value

`DataKind` is a `str` enum: `OBSERVED`, `DERIVED`, `ESTIMATED`, `UNAVAILABLE`.

## Exceptions (`sara_astro.exceptions`)

All inherit from `SaraAstroError`:

- `ObjectNotFoundError(identifier)`
- `CatalogConnectionError(catalog, detail="")`
- `DataUnavailableError`
- `InvalidParameterError`
- `UnsupportedObjectError(identifier, object_type)`

## CLI

```bash
sara-astro <identifier> [--cache/--no-cache]
```

## Not yet implemented (Phase 2+)

`Planet`, `Exoplanet`, `BlackHole`, `sara_astro.physics.relativity`,
`sara_astro.spectroscopy.elements`, VizieR/NASA Exoplanet Archive
adapters, AI-agent tool wrappers.
