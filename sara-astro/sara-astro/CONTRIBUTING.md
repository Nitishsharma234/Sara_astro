# Contributing to SARA Astro

Thanks for considering a contribution.

## Development setup

```bash
git clone https://github.com/Nitishsharma234/sara-astro.git
cd sara-astro
pip install -e ".[dev,cli]"
pytest
```

## Ground rules (please read before opening a PR)

1. **Never fabricate astronomical data.** If a value is unavailable from a
   catalog, return `DataValue.unavailable(...)`. Do not interpolate,
   guess, or hardcode a "reasonable" number.
2. **Every scientific value must carry provenance.** Use `DataValue` with
   an accurate `kind` (`observed` / `derived` / `estimated`) and a
   specific `source` string (name the catalog, or the equation for derived
   values).
3. **Don't reimplement what Astropy/Astroquery already do well.** If
   you're about to write a unit conversion, coordinate transform, or table
   parser from scratch, check whether Astropy already has it first.
4. **Every physics function needs a documented equation and its
   assumptions in the docstring**, and ideally a test against a known
   reference value (e.g. the Sun's own parameters).
5. **New catalog adapters live in `sara_astro/catalogs/`** and should only
   do I/O — translating a catalog response into plain Python/dataclasses.
   They must not raise raw library exceptions; wrap failures in
   `CatalogConnectionError` or `ObjectNotFoundError`.
6. **Tests must not require network access.** Mock catalog calls (see
   `tests/conftest.py` for the pattern) so the suite runs in CI reliably.

## Code style

- Python 3.11+, type hints on public functions
- `black` for formatting, `ruff` for linting: `black . && ruff check .`
- Run `mypy sara_astro` before submitting if you touched typing-sensitive code

## Opening a PR

1. Fork, branch, make your change with tests.
2. Run `pytest` and `black . && ruff check .` locally.
3. Describe what changed and why in the PR description, including which
   scientific equation/source backs any new calculation or field.
