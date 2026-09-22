"""Exception hierarchy for SARA Astro.

All exceptions raised by this library inherit from :class:`SaraAstroError`,
so callers can do::

    try:
        obj = AstroObject("not a real star")
    except SaraAstroError as exc:
        ...

Rather than catching raw ``requests``/``astroquery`` exceptions, every
network or lookup failure is translated into one of these clean, documented
types. Raw tracebacks from underlying libraries are never surfaced to the
end user.
"""

from __future__ import annotations


class SaraAstroError(Exception):
    """Base class for all SARA Astro errors."""


class ObjectNotFoundError(SaraAstroError):
    """Raised when an object name/identifier could not be resolved.

    This means the identification layer queried the available resolvers
    (currently SIMBAD) and none of them recognized the identifier — not
    that a network error occurred (see :class:`CatalogConnectionError`).
    """

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(
            f"Could not resolve '{identifier}' to a known astronomical object."
        )


class CatalogConnectionError(SaraAstroError):
    """Raised when a catalog service could not be reached or errored out.

    This wraps network timeouts, HTTP errors, and malformed responses from
    services such as SIMBAD or Gaia. It does NOT mean the object does not
    exist — it means we couldn't find out.
    """

    def __init__(self, catalog: str, detail: str = "") -> None:
        self.catalog = catalog
        msg = f"Could not reach catalog service '{catalog}'."
        if detail:
            msg += f" Detail: {detail}"
        super().__init__(msg)


class DataUnavailableError(SaraAstroError):
    """Raised when a specific piece of data was requested but does not exist.

    Note: most APIs in this library prefer to return a
    :class:`sara_astro.utils.units.DataValue` with ``kind="unavailable"``
    rather than raising, so the caller isn't forced into try/except for
    normal missing-data situations. This exception is reserved for cases
    where the caller explicitly demanded a value that cannot be produced
    (e.g. calling a physics method that has no fallback).
    """


class InvalidParameterError(SaraAstroError):
    """Raised when a user-supplied parameter is malformed or out of range."""


class UnsupportedObjectError(SaraAstroError):
    """Raised when an object is resolved but its type is not yet supported.

    For example, a resolved object turning out to be a galaxy or nebula in
    an early version of this library that only models stars.
    """

    def __init__(self, identifier: str, object_type: str) -> None:
        self.identifier = identifier
        self.object_type = object_type
        super().__init__(
            f"'{identifier}' was resolved as object type '{object_type}', "
            "which SARA Astro does not yet model."
        )
