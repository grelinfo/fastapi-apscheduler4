"""Test APScheduler Builder."""

from unittest.mock import patch

import pytest

from fastapi_apscheduler4.apscheduler_builder import APSSchedulerBuilder
from fastapi_apscheduler4.config import (
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
    SchedulerConfig,
)
from fastapi_apscheduler4.errors import ConfigNotFoundError, MissingDependencyError


def test_compute_event_broker_type_auto(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute event broker type with auto discovery."""
    # Arrange
    default_builder = APSSchedulerBuilder()
    redis_builder = APSSchedulerBuilder(redis=redis_config)
    postgres_builder = APSSchedulerBuilder(postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(postgres=postgres_config, redis=redis_config)

    # Act
    default_result = default_builder.computed_event_broker_type
    redis_result = redis_builder.computed_event_broker_type
    postgres_result = postgres_builder.computed_event_broker_type
    redis_and_postgres_result = redis_and_postgres_builder.computed_event_broker_type

    # Assert
    assert default_result is EventBrokerType.MEMORY
    assert redis_result is EventBrokerType.REDIS
    assert postgres_result is EventBrokerType.POSTGRES
    assert redis_and_postgres_result is EventBrokerType.REDIS


def test_compute_event_broker_type_redis(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute event broker type for redis."""
    # Arrange
    scheduler = SchedulerConfig(event_broker=EventBrokerType.REDIS)
    default_builder = APSSchedulerBuilder(scheduler=scheduler)
    redis_builder = APSSchedulerBuilder(scheduler=scheduler, redis=redis_config)
    postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config, redis=redis_config)

    # Act
    with pytest.raises(ConfigNotFoundError):
        default_builder.computed_event_broker_type  # noqa: B018
    redis_result = redis_builder.computed_event_broker_type
    with pytest.raises(ConfigNotFoundError):
        postgres_builder.computed_event_broker_type  # noqa: B018
    redis_and_postgres_result = redis_and_postgres_builder.computed_event_broker_type

    # Assert
    assert redis_result is EventBrokerType.REDIS
    assert redis_and_postgres_result is EventBrokerType.REDIS


def test_compute_event_broker_type_postgres(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute event broker type for postgres."""
    # Arrange
    scheduler = SchedulerConfig(event_broker=EventBrokerType.POSTGRES)
    default_builder = APSSchedulerBuilder(scheduler=scheduler)
    redis_builder = APSSchedulerBuilder(scheduler=scheduler, redis=redis_config)
    postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config, redis=redis_config)

    # Act
    with pytest.raises(ConfigNotFoundError):
        default_builder.computed_event_broker_type  # noqa: B018
    with pytest.raises(ConfigNotFoundError):
        redis_builder.computed_event_broker_type  # noqa: B018
    postgres_result = postgres_builder.computed_event_broker_type
    redis_and_postgres_result = redis_and_postgres_builder.computed_event_broker_type

    # Assert
    assert postgres_result is EventBrokerType.POSTGRES
    assert redis_and_postgres_result is EventBrokerType.POSTGRES


def test_compute_event_broker_type_memory(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute event broker type for memory."""
    # Arrange
    scheduler = SchedulerConfig(event_broker=EventBrokerType.MEMORY)
    default_builder = APSSchedulerBuilder(scheduler=scheduler)
    redis_builder = APSSchedulerBuilder(scheduler=scheduler, redis=redis_config)
    postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config, redis=redis_config)

    # Act
    default_result = default_builder.computed_event_broker_type
    redis_result = redis_builder.computed_event_broker_type
    postgres_result = postgres_builder.computed_event_broker_type
    redis_and_postgres_result = redis_and_postgres_builder.computed_event_broker_type

    # Assert
    assert default_result is EventBrokerType.MEMORY
    assert redis_result is EventBrokerType.MEMORY
    assert postgres_result is EventBrokerType.MEMORY
    assert redis_and_postgres_result is EventBrokerType.MEMORY


def test_computed_data_store_type_auto(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute data store type with auto discovery."""
    # Arrange
    default_builder = APSSchedulerBuilder()
    redis_builder = APSSchedulerBuilder(redis=redis_config)
    postgres_builder = APSSchedulerBuilder(postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(postgres=postgres_config, redis=redis_config)

    # Act
    default_result = default_builder.computed_data_store_type
    redis_result = redis_builder.computed_data_store_type
    postgres_result = postgres_builder.computed_data_store_type
    redis_and_postgres_result = redis_and_postgres_builder.computed_data_store_type

    # Assert
    assert default_result is DataStoreType.MEMORY
    assert redis_result is DataStoreType.MEMORY
    assert postgres_result is DataStoreType.POSTGRES
    assert redis_and_postgres_result is DataStoreType.POSTGRES


def test_computed_data_store_type_postgres(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute data store type for postgres."""
    # Arrange
    scheduler = SchedulerConfig(data_store=DataStoreType.POSTGRES)
    default_builder = APSSchedulerBuilder(scheduler=scheduler)
    redis_builder = APSSchedulerBuilder(scheduler=scheduler, redis=redis_config)
    postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config, redis=redis_config)

    # Act
    with pytest.raises(ConfigNotFoundError):
        default_builder.computed_data_store_type  # noqa: B018
    with pytest.raises(ConfigNotFoundError):
        redis_builder.computed_data_store_type  # noqa: B018
    postgres_result = postgres_builder.computed_data_store_type
    redis_and_postgres_result = redis_and_postgres_builder.computed_data_store_type

    # Assert
    assert postgres_result is DataStoreType.POSTGRES
    assert redis_and_postgres_result is DataStoreType.POSTGRES


def test_computed_data_store_type_memory(redis_config: RedisConfig, postgres_config: PostgresConfig) -> None:
    """Test compute data store type for memory."""
    # Arrange
    scheduler = SchedulerConfig(data_store=DataStoreType.MEMORY)
    default_builder = APSSchedulerBuilder(scheduler=scheduler)
    redis_builder = APSSchedulerBuilder(scheduler=scheduler, redis=redis_config)
    postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)
    redis_and_postgres_builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config, redis=redis_config)

    # Act
    default_result = default_builder.computed_data_store_type
    redis_result = redis_builder.computed_data_store_type
    postgres_result = postgres_builder.computed_data_store_type
    redis_and_postgres_result = redis_and_postgres_builder.computed_data_store_type

    # Assert
    assert default_result is DataStoreType.MEMORY
    assert redis_result is DataStoreType.MEMORY
    assert postgres_result is DataStoreType.MEMORY
    assert redis_and_postgres_result is DataStoreType.MEMORY


def test_build_event_broker_redis_missing_dependency(redis_config: RedisConfig) -> None:
    """Test build event broker raises MissingDependencyError when redis package is missing."""
    # Arrange
    scheduler = SchedulerConfig(event_broker=EventBrokerType.REDIS)
    builder = APSSchedulerBuilder(scheduler=scheduler, redis=redis_config)

    # Act & Assert
    with patch("builtins.__import__", side_effect=ImportError("No module named 'redis'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            builder.build_event_broker()

        assert "redis" in str(exc_info.value)
        assert "Redis event broker" in str(exc_info.value)
        assert "redis" in str(exc_info.value)
        assert isinstance(exc_info.value, ImportError)


def test_build_event_broker_postgres_missing_dependency(postgres_config: PostgresConfig) -> None:
    """Test build event broker raises MissingDependencyError when asyncpg package is missing."""
    # Arrange
    scheduler = SchedulerConfig(event_broker=EventBrokerType.POSTGRES)
    builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)

    # Act & Assert
    with patch("builtins.__import__", side_effect=ImportError("No module named 'asyncpg'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            builder.build_event_broker()

        assert "asyncpg" in str(exc_info.value)
        assert "Postgres event broker" in str(exc_info.value)
        assert "postgres" in str(exc_info.value)
        assert isinstance(exc_info.value, ImportError)


def test_build_data_store_postgres_missing_dependency(postgres_config: PostgresConfig) -> None:
    """Test build data store raises MissingDependencyError when sqlalchemy package is missing."""
    # Arrange
    scheduler = SchedulerConfig(data_store=DataStoreType.POSTGRES)
    builder = APSSchedulerBuilder(scheduler=scheduler, postgres=postgres_config)

    # Act & Assert
    with patch("builtins.__import__", side_effect=ImportError("No module named 'sqlalchemy'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            builder.build_data_store()

        assert "sqlalchemy" in str(exc_info.value)
        assert "Postgres data store" in str(exc_info.value)
        assert "postgres" in str(exc_info.value)
        assert isinstance(exc_info.value, ImportError)
