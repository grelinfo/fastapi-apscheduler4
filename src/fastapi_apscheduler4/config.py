"""Configuration models."""

import os
from enum import Enum
from typing import Annotated, cast

from pydantic import (
    AliasChoices,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    model_validator,
)
from pydantic_core import MultiHostUrl, Url
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from fastapi_apscheduler4.constants import API_PAGE_DEFAULT_LIMIT, API_PAGE_MAX_LIMIT
from fastapi_apscheduler4.utils import transform_comma_separated_string_to_list


class _BaseConfig(BaseModel):
    """Base class for config."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class _BaseEnvConfig(BaseSettings):
    """Base class for environment variable config."""

    model_config = SettingsConfigDict(extra="ignore", frozen=True, env_ignore_empty=True)

    @classmethod
    def is_available(cls) -> bool:
        """Check if the environment variables are available.

        Raises:
            ValueError: If `env_prefix` is not set.
        """
        env_prefix = cls.model_config.get("env_prefix")

        if not env_prefix:
            raise ValueError("env_prefix is not set.")  # noqa: TRY003

        return any(key.startswith(env_prefix) for key in os.environ)

    @classmethod
    def create_if_available(cls) -> Self | None:
        """Create the config if the environment variables are available.

        Raises:
            ValueError: If `env_prefix` is not set.
        """
        if cls.is_available():
            return cls()
        return None

    @classmethod
    def from_env(cls) -> Self:
        """Create the config from environment variables.

        Alias for the constructor to avoid type checker issues.

        Raises:
            ValidationError: If the environment variables are not valid.
        """
        return cls()


class EventBrokerType(str, Enum):
    """Scheduler broker."""

    MEMORY = "memory"
    POSTGRES = "postgres"
    REDIS = "redis"


class DataStoreType(str, Enum):
    """Scheduler store."""

    MEMORY = "memory"
    POSTGRES = "postgres"


class PostgresConfig(_BaseConfig):
    """Postgres Config."""

    host: str
    port: int = 5432
    username: str
    password: SecretStr
    db: str

    def get_postgres_dsn(self) -> PostgresDsn:
        """Get Postgres URL."""
        return cast(
            "PostgresDsn",
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.username,
                password=self.password.get_secret_value(),
                host=self.host,
                port=self.port,
                path=self.db,
            ),
        )

    def get_postgres_url(self) -> str:
        """Get Postgres URL."""
        return self.get_postgres_dsn().unicode_string()


class RedisConfig(_BaseConfig):
    """Redis Config."""

    host: str
    port: int = 6379
    username: str
    password: SecretStr
    db: int = 0

    def get_redis_dsn(self) -> RedisDsn:
        """Get the Redis URL."""
        return cast(
            "RedisDsn",
            Url.build(
                scheme="redis",
                username=self.username,
                password=self.password.get_secret_value(),
                host=self.host,
                port=self.port,
                path=str(self.db),
            ),
        )

    def get_redis_url(self) -> str:
        """Get the Redis URL."""
        return self.get_redis_dsn().unicode_string()


class SchedulerConfig(_BaseConfig):
    """Scheduler config."""

    auto_start: bool = True
    event_broker: EventBrokerType | None = None
    data_store: DataStoreType | None = None
    redis_channel: str = "apscheduler"


class SchedulerAPIConfig(_BaseConfig):
    """Scheduler API Config."""

    enabled: bool = True
    prefix: str = "/api/v1"
    tags: Annotated[list[str | Enum] | None, BeforeValidator(transform_comma_separated_string_to_list)] = ["scheduler"]
    include_in_schema: bool = True


class RedisEnvConfig(RedisConfig, _BaseEnvConfig):
    """Redis Environment Config.

    Accept both `REDIS_USER` and `REDIS_USERNAME` environment variables for the username.
    """

    model_config = SettingsConfigDict(env_prefix="REDIS_", validate_by_name=True)

    username: str = Field(validation_alias=AliasChoices("REDIS_USER", "REDIS_USERNAME"))


class PostgresEnvConfig(PostgresConfig, _BaseEnvConfig):
    """Postgres Environment Config.

    Accept both `POSTGRES_USER` and `POSTGRES_USERNAME` environment variables for the username.
    """

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", validate_by_name=True)

    username: str = Field(validation_alias=AliasChoices("POSTGRES_USER", "POSTGRES_USERNAME"))


class SchedulerEnvConfig(SchedulerConfig, _BaseEnvConfig):
    """Scheduler Environment Config."""

    model_config = SettingsConfigDict(env_prefix="SCHEDULER_")


class SchedulerAPIEnvConfig(SchedulerAPIConfig, _BaseEnvConfig):
    """Scheduler API Environment Config."""

    model_config = SettingsConfigDict(env_prefix="SCHEDULER_API_")

    limit_default: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "Page size default limit (only configurable via `SCHEDULER_API_LIMIT_DEFAULT` environment variable)."
            ),
        ),
    ] = API_PAGE_DEFAULT_LIMIT
    limit_max: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "Page size maximum limit (only configurable via `SCHEDULER_API_LIMIT_MAX` environment variable)."
            ),
        ),
    ] = API_PAGE_MAX_LIMIT

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        """Validate that limit_default is less than or equal to limit_max."""
        if self.limit_default > self.limit_max:
            msg = f"limit_default ({self.limit_default}) must be less than or equal to limit_max ({self.limit_max})"
            raise ValueError(msg)
        return self
