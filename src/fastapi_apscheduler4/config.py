"""Configuration models."""

from __future__ import annotations

import os
from enum import Enum
from typing import Annotated, cast

from apscheduler import AsyncScheduler
from pydantic import BaseModel, ConfigDict, Field, PostgresDsn, RedisDsn, SecretStr, computed_field
from pydantic_core import MultiHostUrl, Url
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine


class EventBrokerType(str, Enum):
    """Scheduler broker."""

    MEMORY = "memory"
    POSTGRES = "postgres"
    REDIS = "redis"


class DataStoreType(str, Enum):
    """Scheduler store."""

    MEMORY = "memory"
    POSTGRES = "postgres"


class _BaseConfig(BaseModel):
    """Base Config."""

    model_config = ConfigDict(validate_default=True, arbitrary_types_allowed=True, extra="forbid")


class PostgresConfig(_BaseConfig):
    """Postgres Config."""

    host: str
    port: int = 5432
    user: str | None = None
    password: SecretStr
    db: str

    def get_postgres_dsn(self) -> PostgresDsn:
        """Get Postgres URL."""
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.db,
        )

    def get_postgres_url(self) -> str:
        """Get Postgres URL."""
        return self.get_postgres_dsn().unicode_string()


class RedisConfig(_BaseConfig):
    """Redis Config."""

    host: str
    port: int = 6379
    user: str
    password: SecretStr
    db: int = 0

    def get_redis_dsn(self) -> RedisDsn:
        """Get the Redis URL."""
        return Url.build(
            scheme="redis",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=str(self.db),
        )

    def get_redis_url(self) -> str:
        """Get the Redis URL."""
        return self.get_redis_dsn().unicode_string()


class APIConfig(_BaseConfig):
    """API Config."""

    prefix: str = "/api/v1"
    tags: list[str | Enum] | None = ["scheduler"]
    include_in_schema: bool = True
    limit_default: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "Page size default limit (only configurable via `SCHEDULER_API_LIMIT_DEFAULT` environment variable)."
            ),
        ),
    ] = cast(int, os.getenv("SCHEDULER_API_LIMIT_DEFAULT", "100"))  # validate default enabled
    limit_max: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "Page size maximum limit (only configurable via `SCHEDULER_API_LIMIT_MAX` environment variable)."
            ),
        ),
    ] = cast(int, os.getenv("SCHEDULER_API_LIMIT_MAX", "1000"))  # validate default enabled


class APSchedulerConfig(_BaseConfig):
    """APScheduler config."""

    event_broker: EventBrokerType | None = None
    data_store_store: DataStoreType | None = None

    postgres: PostgresConfig | AsyncEngine | None = None
    redis: RedisConfig | Redis | None = None
    redis_channel: str = "apscheduler"

    @computed_field  # type: ignore[misc] #> mypy issue #1362
    @property
    def computed_event_broker(self) -> EventBrokerType:
        """Computed broker.

        Priority:
        1. Explicit broker.
        2. Redis.
        3. Postgres.
        """
        if not self.event_broker:
            if self.redis:
                return EventBrokerType.REDIS
            if self.postgres:
                return EventBrokerType.POSTGRES
            return EventBrokerType.MEMORY
        return self.event_broker

    @computed_field  # type: ignore[misc] #> mypy issue #1362
    @property
    def computed_data_store(self) -> DataStoreType:
        """Computed store.

        Priority:
        1. Explicit store.
        2. Postgres.
        3. Memory.
        """
        if not self.data_store_store:
            if self.postgres:
                return DataStoreType.POSTGRES
            return DataStoreType.MEMORY
        return self.data_store_store


class SchedulerConfig(_BaseConfig):
    """FastAPI-APScheduler4 config."""

    auto_start: bool = True
    apscheduler: APSchedulerConfig | AsyncScheduler = APSchedulerConfig()
    api: Annotated[APIConfig | None, Field(description="API configuration (None to disable all API routes).")] = (
        APIConfig()
    )
