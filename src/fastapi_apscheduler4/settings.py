"""Settings.

Out-of-the-box settings for FastAPI APScheduler4 that automatically configure the scheduler from environment variables.
"""

from __future__ import annotations

from typing import Any

from pydantic import SecretStr
from pydantic_settings import BaseSettings

from fastapi_apscheduler4.config import DataStoreType, EventBrokerType, SchedulerConfig
from fastapi_apscheduler4.utils import dict_add_if_not_none


class FastAPIAPScheduler4Settings(BaseSettings):
    """FastAPIAPScheduler4 settings from environment variables.

    See `FastAPIAPScheduler4Config` for more details about the default values.
    """

    SCHEDULER_AUTO_START: bool | None = None
    SCHEDULER_BROKER: EventBrokerType | None = None
    SCHEDULER_STORE: DataStoreType | None = None

    SCHEDULER_API_ENABLED: bool = True
    SCHEDULER_API_PREFIX: str | None = None
    SCHEDULER_API_TAGS: list[str] | None = None
    SCHEDULER_API_LIMIT_DEFAULT: int | None = None
    SCHEDULER_API_LIMIT_MAX: int | None = None

    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_DB: str | None = None

    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_USER: str | None = None
    REDIS_PASSWORD: SecretStr | None = None
    REDIS_DB: int | None = None
    SCHEDULER_REDIS_CHANNEL: str | None = None


def create_config_from_env_vars() -> SchedulerConfig:
    """Get the configuration from the environment variables."""
    settings = FastAPIAPScheduler4Settings()

    config: dict[str, Any] = {"apscheduler": {}, "api": None}

    dict_add_if_not_none(config, "auto_start", settings.SCHEDULER_AUTO_START)

    dict_add_if_not_none(config["apscheduler"], "broker", settings.SCHEDULER_BROKER)
    dict_add_if_not_none(config["apscheduler"], "store", settings.SCHEDULER_STORE)

    if settings.POSTGRES_HOST:
        config["postgres"] = {}
        dict_add_if_not_none(config["apscheduler"]["postgres"], "host", settings.POSTGRES_HOST)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "port", settings.POSTGRES_PORT)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "user", settings.POSTGRES_USER)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "password", settings.POSTGRES_PASSWORD)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "db", settings.POSTGRES_DB)

    if settings.REDIS_HOST:
        config["redis"] = {}
        dict_add_if_not_none(config["apscheduler"]["redis"], "host", settings.REDIS_HOST)
        dict_add_if_not_none(config["apscheduler"]["redis"], "port", settings.REDIS_PORT)
        dict_add_if_not_none(config["apscheduler"]["redis"], "user", settings.REDIS_USER)
        dict_add_if_not_none(config["apscheduler"]["redis"], "password", settings.REDIS_PASSWORD)
        dict_add_if_not_none(config["apscheduler"]["redis"], "db", settings.REDIS_DB)
        dict_add_if_not_none(config["apscheduler"], "redis_channel", settings.SCHEDULER_REDIS_CHANNEL)

    if settings.SCHEDULER_API_ENABLED:
        config["api"] = {}
        dict_add_if_not_none(config["api"], "prefix", settings.SCHEDULER_API_PREFIX)
        dict_add_if_not_none(config["api"], "tags", settings.SCHEDULER_API_TAGS)
        dict_add_if_not_none(config["api"], "limit_default", settings.SCHEDULER_API_LIMIT_DEFAULT)
        dict_add_if_not_none(config["api"], "limit_max", settings.SCHEDULER_API_LIMIT_MAX)

    return SchedulerConfig.model_validate(config)
