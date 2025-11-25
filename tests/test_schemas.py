"""Test Schemas."""

import pytest
from pydantic import BaseModel, ValidationError

from fastapi_apscheduler4.schemas import TimeZoneName


class SampleTimezone(BaseModel):
    """Sample model with timezone field."""

    timezone: TimeZoneName


@pytest.mark.parametrize(
    ("timezone_value", "expected"),
    [
        ("Europe/Zurich", "Europe/Zurich"),
        ("America/New_York", "America/New_York"),
        ("Europe/Paris", "Europe/Paris"),
        ("Asia/Tokyo", "Asia/Tokyo"),
        ("UTC", "UTC"),
    ],
    ids=["europe_zurich", "america_new_york", "europe_paris", "asia_tokyo", "utc"],
)
def test_timezone_valid(timezone_value: TimeZoneName, expected: str) -> None:
    """Test Timezone schema with valid timezone values."""
    # Arrange & Act
    model = SampleTimezone(timezone=timezone_value)

    # Assert
    assert model.timezone == expected
    assert isinstance(model.timezone, str)


@pytest.mark.parametrize(
    "invalid_timezone",
    [
        "Invalid/Timezone",
        "NotATimezone",
        "America/FakeCity",
        "",
    ],
    ids=["invalid_format", "not_a_timezone", "fake_city", "empty_string"],
)
def test_timezone_invalid(invalid_timezone: TimeZoneName) -> None:
    """Test Timezone schema raises ValidationError for invalid timezones."""
    # Arrange & Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        SampleTimezone(timezone=invalid_timezone)

    # Assert - verify the error is about timezone validation
    assert "timezone" in str(exc_info.value).lower()
