from __future__ import annotations

import pytest

from sara_astro.exceptions import InvalidParameterError
from sara_astro.utils.validation import require_positive, sanitize_identifier


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Sirius", "Sirius"),
        ("  HD 48915  ", "HD 48915"),
        ("HIP   32349", "HIP 32349"),
        ("Gaia DR3 123456789", "Gaia DR3 123456789"),
    ],
)
def test_sanitize_identifier_normalizes(raw, expected):
    assert sanitize_identifier(raw) == expected


def test_sanitize_identifier_rejects_empty():
    with pytest.raises(InvalidParameterError):
        sanitize_identifier("   ")


def test_sanitize_identifier_rejects_non_string():
    with pytest.raises(InvalidParameterError):
        sanitize_identifier(12345)  # type: ignore[arg-type]


def test_sanitize_identifier_rejects_bad_characters():
    with pytest.raises(InvalidParameterError):
        sanitize_identifier("Sirius; DROP TABLE stars;")


def test_require_positive_accepts_valid():
    assert require_positive(2.0, "mass") == 2.0


@pytest.mark.parametrize("bad_value", [0, -1, float("nan"), float("inf")])
def test_require_positive_rejects_invalid(bad_value):
    with pytest.raises(InvalidParameterError):
        require_positive(bad_value, "mass")


def test_require_positive_rejects_non_numeric():
    with pytest.raises(InvalidParameterError):
        require_positive("not a number", "mass")  # type: ignore[arg-type]
