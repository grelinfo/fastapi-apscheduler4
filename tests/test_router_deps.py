"""Test FastAPI Dependencies."""

import pytest

from fastapi_apscheduler4.config import SchedulerAPIEnvConfig
from fastapi_apscheduler4.constants import API_PAGE_DEFAULT_LIMIT, API_PAGE_MAX_LIMIT
from fastapi_apscheduler4.dtos import LimitOffset
from fastapi_apscheduler4.routers.deps import get_scheduler_api_config, limit_offset


def test_get_scheduler_api_config() -> None:
    """Test get_scheduler_api_config returns config instance."""
    # Act
    config = get_scheduler_api_config()

    # Assert
    assert isinstance(config, SchedulerAPIEnvConfig)
    assert config.limit_default == API_PAGE_DEFAULT_LIMIT
    assert config.limit_max == API_PAGE_MAX_LIMIT


def test_get_scheduler_api_config_is_cached() -> None:
    """Test get_scheduler_api_config returns same instance (lru_cache)."""
    # Act
    config1 = get_scheduler_api_config()
    config2 = get_scheduler_api_config()

    # Assert
    assert config1 is config2


def test_limit_offset_with_default_limit() -> None:
    """Test limit_offset uses config default when limit is None."""
    # Arrange
    config = get_scheduler_api_config()

    # Act
    result = limit_offset(config=config, limit=None, offset=0)

    # Assert
    assert isinstance(result, LimitOffset)
    assert result.limit == config.limit_default
    assert result.offset == 0


def test_limit_offset_with_explicit_limit() -> None:
    """Test limit_offset uses provided limit when valid."""
    # Arrange
    config = get_scheduler_api_config()
    explicit_limit = 50
    explicit_offset = 10

    # Act
    result = limit_offset(config=config, limit=explicit_limit, offset=explicit_offset)

    # Assert
    assert result.limit == explicit_limit
    assert result.offset == explicit_offset


def test_limit_offset_caps_at_max() -> None:
    """Test limit_offset caps limit at config.limit_max."""
    # Arrange
    config = get_scheduler_api_config()
    over_max_limit = config.limit_max + 500

    # Act
    result = limit_offset(config=config, limit=over_max_limit, offset=0)

    # Assert
    assert result.limit == config.limit_max
    assert result.offset == 0


def test_limit_offset_with_custom_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test limit_offset respects custom config values from environment."""
    # Arrange
    custom_default = 25
    custom_max = 200
    over_limit = 300

    get_scheduler_api_config.cache_clear()
    monkeypatch.setenv("SCHEDULER_API_LIMIT_DEFAULT", str(custom_default))
    monkeypatch.setenv("SCHEDULER_API_LIMIT_MAX", str(custom_max))
    config = get_scheduler_api_config()

    # Act
    result_default = limit_offset(config=config, limit=None, offset=0)
    result_capped = limit_offset(config=config, limit=over_limit, offset=0)

    # Assert
    assert result_default.limit == custom_default
    assert result_capped.limit == custom_max

    # Cleanup
    get_scheduler_api_config.cache_clear()


def test_limit_offset_with_various_offsets() -> None:
    """Test limit_offset handles different offset values."""
    # Arrange
    config = get_scheduler_api_config()
    test_limit = 10
    zero_offset = 0
    medium_offset = 100
    large_offset = 999

    # Act & Assert
    result1 = limit_offset(config=config, limit=test_limit, offset=zero_offset)
    assert result1.offset == zero_offset

    result2 = limit_offset(config=config, limit=test_limit, offset=medium_offset)
    assert result2.offset == medium_offset

    result3 = limit_offset(config=config, limit=test_limit, offset=large_offset)
    assert result3.offset == large_offset


def test_limit_offset_with_none_config() -> None:
    """Test limit_offset handles None config by using default."""
    # Arrange
    test_limit = 50
    test_offset = 10

    # Act
    result = limit_offset(config=None, limit=test_limit, offset=test_offset)  # type: ignore[arg-type]

    # Assert
    assert result.limit == test_limit
    assert result.offset == test_offset
