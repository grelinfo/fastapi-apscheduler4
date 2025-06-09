"""APScheduler Builder."""

from functools import cached_property

from apscheduler import AsyncScheduler
from apscheduler.abc import DataStore, EventBroker
from pydantic import BaseModel, ConfigDict, Field, computed_field

from fastapi_apscheduler4.config import (
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    PostgresEnvConfig,
    RedisConfig,
    RedisEnvConfig,
    SchedulerConfig,
    SchedulerEnvConfig,
)
from fastapi_apscheduler4.errors import ConfigNotFoundError


class APSSchedulerBuilder(BaseModel):
    """APSScheduler Builder.

    Build APScheduler Async Scheduler, data store, and event broker based on the provided configurations.

    If not explicitly provided in the scheduler config, the data store and event broker types are computed as follows:
    - Data store: Postgres if available, otherwise Memory.
    - Event broker: Redis if available, Postgres if available, otherwise Memory.
    """

    model_config = ConfigDict(frozen=True, validate_default=True, extra="forbid")

    scheduler: SchedulerConfig = Field(default_factory=SchedulerEnvConfig)
    redis: RedisConfig | None = Field(default_factory=RedisEnvConfig.create_if_available)
    postgres: PostgresConfig | None = Field(default_factory=PostgresEnvConfig.create_if_available)

    @computed_field()  # type: ignore[prop-decorator]
    @cached_property
    def computed_data_store_type(self) -> DataStoreType:
        """Computed data store type."""
        if self.scheduler.data_store:
            if self.scheduler.data_store is DataStoreType.POSTGRES and not self.postgres:
                raise ConfigNotFoundError("postgres", "Required for Postgres data store.")
            return self.scheduler.data_store
        if self.postgres:
            return DataStoreType.POSTGRES
        return DataStoreType.MEMORY

    @computed_field()  # type: ignore[prop-decorator]
    @cached_property
    def computed_event_broker_type(self) -> EventBrokerType:
        """Computed event broker type."""
        if self.scheduler.event_broker:
            if self.scheduler.event_broker is EventBrokerType.REDIS and not self.redis:
                raise ConfigNotFoundError("redis", "Required for Redis event broker.")
            if self.scheduler.event_broker is EventBrokerType.POSTGRES and not self.postgres:
                raise ConfigNotFoundError("postgres", "Required for Postgres event broker.")
            return self.scheduler.event_broker
        if self.redis:
            return EventBrokerType.REDIS
        if self.postgres:
            return EventBrokerType.POSTGRES
        return EventBrokerType.MEMORY

    def build(self) -> AsyncScheduler:
        """Create APScheduler Async Scheduler."""
        return AsyncScheduler(
            data_store=self.build_data_store(),
            event_broker=self.build_event_broker(),
        )

    def build_event_broker(self) -> EventBroker:
        """Build APScheduler event broker."""
        broker_type = self.computed_event_broker_type

        if broker_type is EventBrokerType.REDIS:
            # Lazy imports to avoid Redis dependency
            from apscheduler.eventbrokers.redis import RedisEventBroker

            if not self.redis:
                raise ConfigNotFoundError("redis", "Required for Redis event broker.")

            return RedisEventBroker(self.redis.get_redis_url(), channel=self.scheduler.redis_channel)

        if broker_type is EventBrokerType.POSTGRES:
            # Lazy imports to avoid SQLAlchemy dependency
            from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

            if not self.postgres:
                raise ConfigNotFoundError("postgres", "Required for Postgres event broker.")

            return AsyncpgEventBroker(dsn=self.postgres.get_postgres_url())

        if broker_type is EventBrokerType.MEMORY:
            from apscheduler.eventbrokers.local import LocalEventBroker

            return LocalEventBroker()

        # Replace with assert_never(broker_type) when Python 3.11 is the minimum supported version
        msg = f"Unexpected event broker type: {broker_type}"
        raise AssertionError(msg)

    def build_data_store(self) -> DataStore:
        """Build APScheduler data store."""
        data_store_type = self.computed_data_store_type

        if data_store_type is DataStoreType.POSTGRES:
            # Lazy imports to avoid SQLAlchemy dependency
            from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore

            if not self.postgres:
                raise ConfigNotFoundError("postgres", "Required for Postgres data store.")

            return SQLAlchemyDataStore(self.postgres.get_postgres_url())

        if data_store_type is DataStoreType.MEMORY:
            from apscheduler.datastores.memory import MemoryDataStore

            return MemoryDataStore()

        # Replace with assert_never(data_store_type) when Python 3.11 is the minimum supported version
        msg = f"Unexpected data store type: {data_store_type}"
        raise AssertionError(msg)
