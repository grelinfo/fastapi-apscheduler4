"""Test Settings."""

import pytest
from fastapi_apscheduler4.config import (
    APIConfig,
    APSchedulerConfig,
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
    SchedulerConfig,
)
from fastapi_apscheduler4.settings import get_config_from_env_vars
from pydantic import SecretStr


def test_settings_config_default() -> None:
    """Test create config from environment variables."""
    # Arrange
    expected_config = SchedulerConfig()

    # Act
    config = get_config_from_env_vars()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_settings_config_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create config from environment variables with PostgreSQL."""
    # Arrange
    expected_config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            postgres=PostgresConfig(
                host="localhost",
                db="test",
                user="test",
                password=SecretStr("test"),
            )
        )
    )
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_DB", "test")
    monkeypatch.setenv("POSTGRES_USER", "test")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test")

    # Act
    config = get_config_from_env_vars()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_settings_config_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create config from environment variables with Redis."""
    # Arrange
    expected_config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            redis=RedisConfig(host="localhost", user="test", password=SecretStr("test")),
        )
    )
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_USER", "test")
    monkeypatch.setenv("REDIS_PASSWORD", "test")

    # Act
    config = get_config_from_env_vars()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_settings_config_api(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create config from environment variables with API."""
    # Arrange
    expected_config = SchedulerConfig(
        api=APIConfig(
            prefix="api/v2",
            tags=["apscheduler", "scheduler"],
            include_in_schema=False,
            limit_default=50,
            limit_max=500,
        )
    )
    monkeypatch.setenv("SCHEDULER_API_PREFIX", "api/v2")
    monkeypatch.setenv("SCHEDULER_API_TAGS", "apscheduler,scheduler")
    monkeypatch.setenv("SCHEDULER_API_INCLUDE_IN_SCHEMA", "false")
    monkeypatch.setenv("SCHEDULER_API_LIMIT_DEFAULT", "50")
    monkeypatch.setenv("SCHEDULER_API_LIMIT_MAX", "500")

    # Act
    config = get_config_from_env_vars()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_settings_config_api_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create config from environment variables with API disabled."""
    # Arrange
    expected_config = SchedulerConfig(api=APIConfig(enabled=False))
    monkeypatch.setenv("SCHEDULER_API_ENABLED", "false")

    # Act
    config = get_config_from_env_vars()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_settings_config_data_store_and_event_broker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create config from environment variables with data store and event broker."""
    # Arrange
    expected_config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            data_store=DataStoreType.POSTGRES,
            event_broker=EventBrokerType.POSTGRES,
        )
    )

    monkeypatch.setenv("SCHEDULER_EVENT_BROKER", "postgres")
    monkeypatch.setenv("SCHEDULER_DATA_STORE", "postgres")

    # Act
    config = get_config_from_env_vars()

    # Assert
    assert config.model_dump() == expected_config.model_dump()
