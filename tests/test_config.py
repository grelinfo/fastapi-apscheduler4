"""Test Config."""

from fastapi_apscheduler4.config import (
    APSchedulerConfig,
    PostgresConfig,
    RedisConfig,
    SchedulerConfig,
)
from pydantic import SecretStr


def test_config_broker() -> None:
    """Test config broker."""
    # Arrange & Act
    config_auto_memory = SchedulerConfig()
    config_auto_postgres_config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            postgres=PostgresConfig(
                host="localhost",
                db="test",
                user="test",
                password=SecretStr("test"),
            )
        )
    )
    config_auto_redis = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            redis=RedisConfig(host="localhost", user="test", password=SecretStr("test")),
        )
    )

    # Assert
    assert config_auto_memory.apscheduler is None
    assert isinstance(config_auto_postgres_config.apscheduler, APSchedulerConfig)
    assert isinstance(config_auto_redis.apscheduler, APSchedulerConfig)


def test_config_store() -> None:
    """Test config store."""
    # Arrange & Act
    config_auto_memory = SchedulerConfig(apscheduler=APSchedulerConfig())
    config_auto_postgres = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            postgres=PostgresConfig(
                host="localhost",
                db="test",
                user="test",
                password=SecretStr("test"),
            )
        )
    )

    # Assert
    assert isinstance(config_auto_memory.apscheduler, APSchedulerConfig)
    assert isinstance(config_auto_postgres.apscheduler, APSchedulerConfig)
