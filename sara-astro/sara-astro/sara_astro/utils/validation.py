"""Input sanitizing and identifier-format helpers.

These are deliberately conservative: they reject obviously malformed input
early with a clean :class:`~sara_astro.exceptions.InvalidParameterError`
rather than letting a mangled string reach a catalog query and come back as
a confusing network error.
"""

from __future__ import annotations

import math
import re

from sara_astro.exceptions import InvalidParameterError

_MAX_NAME_LENGTH = 200

# A permissive allowlist: letters, digits, spaces, and the punctuation that
# legitimately appears in astronomical designations (e.g. "HD 189733 b",
# "Gaia DR3 123456789", "V* alf CMa", "PSR B1919+21").
_ALLOWED_CHARS = re.compile(r"^[A-Za-z0-9\s\+\-\.\*\'/]+$")


def sanitize_identifier(identifier: str) -> str:
    """Validate and normalize a user-supplied object identifier.

    Args:
        identifier: The raw string passed by the user, e.g. ``"Sirius"``
            or ``" hd 189733 "``.

    Returns:
        The identifier stripped of surrounding whitespace, with internal
        whitespace collapsed.

    Raises:
        InvalidParameterError: if ``identifier`` is empty, too long, or
            contains characters that cannot plausibly appear in a real
            astronomical designation.
    """
    if not isinstance(identifier, str):
        raise InvalidParameterError(
            f"Object identifier must be a string, got {type(identifier).__name__}."
        )

    cleaned = " ".join(identifier.split())

    if not cleaned:
        raise InvalidParameterError("Object identifier cannot be empty.")

    if len(cleaned) > _MAX_NAME_LENGTH:
        raise InvalidParameterError(
            f"Object identifier is too long ({len(cleaned)} chars, "
            f"max {_MAX_NAME_LENGTH})."
        )

    if not _ALLOWED_CHARS.match(cleaned):
        raise InvalidParameterError(
            f"Object identifier '{identifier}' contains characters that are "
            "not valid in an astronomical designation."
        )

    return cleaned


def require_positive(value: float, name: str) -> float:
    """Raise if ``value`` is not a positive, finite number."""
    if value is None:
        raise InvalidParameterError(f"'{name}' must be provided.")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise InvalidParameterError(f"'{name}' must be numeric.") from exc
    if math.isnan(numeric) or math.isinf(numeric):
        raise InvalidParameterError(f"'{name}' must be a finite number.")
    if numeric <= 0:
        raise InvalidParameterError(f"'{name}' must be positive, got {numeric}.")
    return numeric
