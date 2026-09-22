# Changelog

All notable changes to this project are documented here.

## [0.1.0] — Phase 1 MVP

### Added
- `AstroObject`: catalog-backed (SIMBAD + best-effort Gaia DR3) unified object interface — `.identifiers()`, `.position()`, `.distance()`, `.photometry()`, `.physical_properties()`, `.available_data()`, `.info()`
- `Star`: extends `AstroObject` with online catalog mode and a fully offline mode (`Star(mass=..., radius=..., temperature=...)`)
- Stellar physics: `surface_gravity()`, `density()`, `escape_velocity()`, `luminosity()` (Stefan-Boltzmann)
- `identification.resolver`: name/ID → canonical cross-identifier set (SIMBAD, HIP, HD, TYC, Gaia DR3)
- `utils.units.DataValue`: provenance-carrying value wrapper (`observed`/`derived`/`estimated`/`unavailable`), with unit-conversion support via Astropy units
- `utils.cache`: minimal opt-in on-disk cache for catalog responses
- Clean exception hierarchy (`ObjectNotFoundError`, `CatalogConnectionError`, `InvalidParameterError`, `DataUnavailableError`, `UnsupportedObjectError`)
- Basic CLI: `sara-astro <identifier>`
- Full offline-mockable test suite (pytest)
- Packaging via `pyproject.toml` (hatchling), installable with `pip install -e .`

### Known limitations (see README "Scientific limitations")
- Stellar mass is not populated automatically in online mode (rarely available from SIMBAD/Gaia for single stars); calculations needing mass will report `unavailable` unless supplied via offline `Star(...)`.
- No Planet/Exoplanet/BlackHole modules yet.
- No spectroscopy/elemental-abundance support yet.
