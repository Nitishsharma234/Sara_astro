# SARA Astro

**Scientific Astronomy Research & Analysis**

A unified, higher-level Python interface for working with astronomical
objects — built *on top of* Astropy, Astroquery, SIMBAD, and Gaia, not as
a replacement for them.

```python
from sara_astro import AstroObject

obj = AstroObject("Sirius")
print(obj.info())
```

```text
Object: * alf CMa

Identifiers:
  SIMBAD: * alf CMa
  Gaia DR3: 2947050466531873024
  HIP: 32349
  HD: 48915

Position:
  RA:  101.287... deg [observed, source: SIMBAD]
  DEC: -16.716... deg [observed, source: SIMBAD]

Distance:
  2.637... ± 0.011 pc [derived, source: derived from Gaia DR3 parallax (d = 1000/plx_mas)]

Physical properties:
  Temperature: 9940.0 K [estimated, source: Gaia DR3 (GSP-Phot)]
  Radius: 1.71 solRad [estimated, source: Gaia DR3 (GSP-Phot)]

Spectral type: A0m... [observed, source: SIMBAD]
```

## Problem statement

Information about a single astronomical object is scattered across
catalogs — Gaia, SIMBAD, HIP, HD, and others each know a different subset
of facts about it, under different identifiers, in different units, with
different (or no) uncertainty estimates. Existing tools (Astropy,
Astroquery) give you excellent low-level access to each of those sources
individually, but nothing gives you *one object* with everything currently
knowable about it, tagged with where each fact came from.

SARA Astro is that integration and analysis layer.

## Installation

```bash
pip install sara-astro
```

Or, for local development:

```bash
git clone https://github.com/Nitishsharma234/sara-astro.git
cd sara-astro
pip install -e ".[dev,cli]"
```

See [INSTALLATION.md](INSTALLATION.md) for details.

## Quick example

```python
from sara_astro import AstroObject, Star

# Catalog-backed
obj = AstroObject("Betelgeuse")
print(obj.identifiers())
print(obj.distance())
print(obj.physical_properties())

# Fully offline — no network, pure physics
sun = Star(mass=1.0, radius=1.0, temperature=5772.0)
print(sun.luminosity())
print(sun.surface_gravity())
```

See [QUICKSTART.md](QUICKSTART.md) for a walkthrough.

## Supported objects (current status)

| Object type | Status |
|---|---|
| Star (catalog-backed via SIMBAD/Gaia) | ✅ Phase 1 |
| Star (offline physics from manual params) | ✅ Phase 1 |
| Planet | 🔜 Phase 2 |
| Exoplanet (NASA Exoplanet Archive) | 🔜 Phase 2 |
| Black hole | 🔜 Phase 2 |

## Data sources

- [SIMBAD](https://simbad.u-strasbg.fr/simbad/) — object identification, cross-identifiers, spectral type, photometry, parallax
- [Gaia DR3](https://www.cosmos.esa.int/web/gaia/dr3) — parallax, astrophysical parameter estimates (temperature, radius)
- (Planned) VizieR, NASA Exoplanet Archive

## Scientific limitations — please read

- **We do not invent data.** If a catalog does not report a value, SARA
  Astro returns a `DataValue` with `kind="unavailable"` — never a fake or
  interpolated number.
- **Provenance is mandatory.** Every value carries `kind` (`observed` /
  `derived` / `estimated` / `unavailable`) and a `source` string. Gaia's
  `teff_gspphot`/`radius_gspphot`, for example, are model-based estimates,
  not direct observations, and are labeled accordingly.
- **Mass is often unavailable.** Stellar mass generally requires a binary
  orbit solution or an evolutionary-model fit; it is not a standard SIMBAD
  or Gaia field. Calculations that need mass (surface gravity, escape
  velocity, mean density) will report `unavailable` for most single stars
  in online mode. Use offline `Star(mass=..., radius=..., ...)` if you
  have a mass from elsewhere.
- **No elemental abundance from a name.** Chemical composition requires
  actual spectroscopic data, which is out of scope for Phase 1 (see
  `sara_astro/spectroscopy`, not yet implemented).

## Roadmap

- Phase 2: Planet/Exoplanet/BlackHole modules, VizieR + NASA Exoplanet Archive, relativity module, spectroscopy module
- Phase 3: Optional AI-agent-facing tool wrappers (`get_object_info()`, etc.) as a separate, non-core module

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
