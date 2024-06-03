"""Test Config."""

from fastapi_apscheduler4.config import (
    APSchedulerConfig,
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
    SchedulerConfig,
)
from pydantic import SecretStr
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine


def test_broker_auto() -> None:
    """Test broker auto."""
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
    config_auto_postgres_engine = SchedulerConfig(
        apscheduler=APSchedulerConfig(postgres=create_async_engine("postgresql+asyncpg://test:test@localhost/test"))
    )
    config_auto_redis_config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            redis=RedisConfig(host="localhost", user="test", password=SecretStr("test")),
        )
    )
    config_auto_redis_client = SchedulerConfig(
        apscheduler=APSchedulerConfig(redis=Redis.from_url("redis://test:test@localhost:6379/0"))
    )

    # Assert
    assert isinstance(config_auto_memory.apscheduler, APSchedulerConfig)
    assert config_auto_memory.apscheduler.computed_event_broker == EventBrokerType.MEMORY
    assert isinstance(config_auto_postgres_config.apscheduler, APSchedulerConfig)
    assert config_auto_postgres_config.apscheduler.computed_event_broker == EventBrokerType.POSTGRES
    assert isinstance(config_auto_postgres_engine.apscheduler, APSchedulerConfig)
    assert config_auto_postgres_engine.apscheduler.computed_event_broker == EventBrokerType.POSTGRES
    assert isinstance(config_auto_redis_config.apscheduler, APSchedulerConfig)
    assert config_auto_redis_config.apscheduler.computed_event_broker == EventBrokerType.REDIS
    assert isinstance(config_auto_redis_client.apscheduler, APSchedulerConfig)
    assert config_auto_redis_client.apscheduler.computed_event_broker == EventBrokerType.REDIS


def test_store_auto() -> None:
    """Test store auto."""
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
    config_auto_postgres_engine = SchedulerConfig(
        apscheduler=APSchedulerConfig(postgres=create_async_engine("postgresql+asyncpg://test:test@localhost/test"))
    )

    # Assert
    assert isinstance(config_auto_memory.apscheduler, APSchedulerConfig)
    assert config_auto_memory.apscheduler.computed_data_store == DataStoreType.MEMORY
    assert isinstance(config_auto_postgres_config.apscheduler, APSchedulerConfig)
    assert config_auto_postgres_config.apscheduler.computed_data_store == DataStoreType.POSTGRES
    assert isinstance(config_auto_postgres_engine.apscheduler, APSchedulerConfig)
    assert config_auto_postgres_engine.apscheduler.computed_data_store == DataStoreType.POSTGRES
