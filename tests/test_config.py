"""Test configuration."""

import pytest
from pydantic import SecretStr

from fastapi_apscheduler4.config import (
    PostgresConfig,
    PostgresEnvConfig,
    RedisConfig,
    RedisEnvConfig,
    SchedulerAPIEnvConfig,
    SchedulerConfig,
    SchedulerEnvConfig,
)


def test_config_default() -> None:
    """Test create scheduler config from environment variables."""
    # Arrange
    expected_config = SchedulerConfig()

    # Act
    config = SchedulerEnvConfig()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


@pytest.mark.parametrize("username", ["USER", "USERNAME"])
def test_postgres_env_config(monkeypatch: pytest.MonkeyPatch, postgres_config: PostgresConfig, username: str) -> None:
    """Test create postgres config from environment variables."""
    # Arrange
    monkeypatch.setenv("POSTGRES_HOST", postgres_config.host)
    monkeypatch.setenv("POSTGRES_DB", postgres_config.db)
    monkeypatch.setenv(f"POSTGRES_{username}", postgres_config.username)
    monkeypatch.setenv("POSTGRES_PASSWORD", postgres_config.password.get_secret_value())

    # Act
    config = PostgresEnvConfig()

    # Assert
    assert config.model_dump() == postgres_config.model_dump()


def test_redis_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create redis config from environment variables."""
    # Arrange
    expected_config = RedisConfig(host="localhost", username="test", password=SecretStr("test"))
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_USER", "test")
    monkeypatch.setenv("REDIS_PASSWORD", "test")

    # Act
    config = RedisEnvConfig()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_config_api(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create api config from environment variables."""
    # Arrange
    expected_config = SchedulerAPIEnvConfig(
        prefix="api/v2",
        tags=["apscheduler", "scheduler"],
        include_in_schema=False,
        limit_default=50,
        limit_max=500,
    )

    monkeypatch.setenv("SCHEDULER_API_PREFIX", "api/v2")
    monkeypatch.setenv("SCHEDULER_API_TAGS", "apscheduler,scheduler")
    monkeypatch.setenv("SCHEDULER_API_INCLUDE_IN_SCHEMA", "false")
    monkeypatch.setenv("SCHEDULER_API_LIMIT_DEFAULT", "50")
    monkeypatch.setenv("SCHEDULER_API_LIMIT_MAX", "500")

    # Act
    config = SchedulerAPIEnvConfig()

    # Assert
    assert config.model_dump() == expected_config.model_dump()


def test_config_api_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test create config from environment variables with API disabled."""
    # Arrange
    expected_config = SchedulerAPIEnvConfig(enabled=False)
    monkeypatch.setenv("SCHEDULER_API_ENABLED", "false")

    # Act
    config = SchedulerAPIEnvConfig()

    # Assert
    assert config.model_dump() == expected_config.model_dump()
