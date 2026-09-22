"""SARA Astro — Scientific Astronomy Research & Analysis.

A unified, higher-level Python interface over public astronomy catalogs
(SIMBAD, Gaia, ...) and the existing scientific Python astronomy stack
(Astropy, Astroquery). SARA Astro does not replace those libraries — it
integrates them behind one object-oriented API with explicit data
provenance (observed / derived / estimated / unavailable) on every value.

Quick start:
    >>> from sara_astro import AstroObject
    >>> obj = AstroObject("Sirius")   # doctest: +SKIP
    >>> print(obj.info())              # doctest: +SKIP
"""

from sara_astro.exceptions import (
    CatalogConnectionError,
    DataUnavailableError,
    InvalidParameterError,
    ObjectNotFoundError,
    SaraAstroError,
    UnsupportedObjectError,
)
from sara_astro.objects.base import AstroObject
from sara_astro.objects.star import Star
from sara_astro.utils.units import DataKind, DataValue

__version__ = "0.1.0"

__all__ = [
    "AstroObject",
    "CatalogConnectionError",
    "DataKind",
    "DataUnavailableError",
    "DataValue",
    "InvalidParameterError",
    "ObjectNotFoundError",
    "SaraAstroError",
    "Star",
    "UnsupportedObjectError",
    "__version__",
]
