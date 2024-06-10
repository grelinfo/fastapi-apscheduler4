"""Settings.

Out-of-the-box settings for FastAPI APScheduler4 that automatically configure the scheduler from environment variables.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator, SecretStr
from pydantic_settings import BaseSettings

from fastapi_apscheduler4.config import DataStoreType, EventBrokerType, SchedulerConfig
from fastapi_apscheduler4.utils import dict_add_if_not_none, transform_coma_separated_string_to_list


class SchedulerSettings(BaseSettings):
    """FastAPIAPScheduler4 settings from environment variables.

    See `FastAPIAPScheduler4Config` for more details about the default values.
    """

    SCHEDULER_AUTO_START: bool | None = None
    SCHEDULER_EVENT_BROKER: EventBrokerType | None = None
    SCHEDULER_DATA_STORE: DataStoreType | None = None

    SCHEDULER_API_ENABLED: bool = True
    SCHEDULER_API_PREFIX: str | None = None
    SCHEDULER_API_TAGS: Annotated[list[str] | None, BeforeValidator(transform_coma_separated_string_to_list)] = None
    SCHEDULER_API_LIMIT_DEFAULT: int | None = None
    SCHEDULER_API_LIMIT_MAX: int | None = None
    SCHEDULER_API_INCLUDE_IN_SCHEMA: bool | None = None

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


def get_config_from_env_vars() -> SchedulerConfig:
    """Get the configuration from the environment variables."""
    settings = SchedulerSettings()

    config: dict[str, Any] = {}

    dict_add_if_not_none(config, "auto_start", settings.SCHEDULER_AUTO_START)

    if settings.SCHEDULER_EVENT_BROKER or settings.SCHEDULER_DATA_STORE:
        config["apscheduler"] = {}
        dict_add_if_not_none(config["apscheduler"], "event_broker", settings.SCHEDULER_EVENT_BROKER)
        dict_add_if_not_none(config["apscheduler"], "data_store", settings.SCHEDULER_DATA_STORE)

    if settings.POSTGRES_HOST:
        config["apscheduler"] = config.get("apscheduler", {})
        config["apscheduler"]["postgres"] = {}
        dict_add_if_not_none(config["apscheduler"]["postgres"], "host", settings.POSTGRES_HOST)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "port", settings.POSTGRES_PORT)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "username", settings.POSTGRES_USER)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "password", settings.POSTGRES_PASSWORD)
        dict_add_if_not_none(config["apscheduler"]["postgres"], "dbname", settings.POSTGRES_DB)

    if settings.REDIS_HOST:
        config["apscheduler"] = config.get("apscheduler", {})
        config["apscheduler"]["redis"] = {}
        dict_add_if_not_none(config["apscheduler"]["redis"], "host", settings.REDIS_HOST)
        dict_add_if_not_none(config["apscheduler"]["redis"], "port", settings.REDIS_PORT)
        dict_add_if_not_none(config["apscheduler"]["redis"], "username", settings.REDIS_USER)
        dict_add_if_not_none(config["apscheduler"]["redis"], "password", settings.REDIS_PASSWORD)
        dict_add_if_not_none(config["apscheduler"]["redis"], "db", settings.REDIS_DB)
        dict_add_if_not_none(config["apscheduler"]["redis"], "channel", settings.SCHEDULER_REDIS_CHANNEL)

    config["api"] = {}
    dict_add_if_not_none(config["api"], "enabled", settings.SCHEDULER_API_ENABLED)
    dict_add_if_not_none(config["api"], "prefix", settings.SCHEDULER_API_PREFIX)
    dict_add_if_not_none(config["api"], "tags", settings.SCHEDULER_API_TAGS)
    dict_add_if_not_none(config["api"], "limit_default", settings.SCHEDULER_API_LIMIT_DEFAULT)
    dict_add_if_not_none(config["api"], "limit_max", settings.SCHEDULER_API_LIMIT_MAX)
    dict_add_if_not_none(config["api"], "include_in_schema", settings.SCHEDULER_API_INCLUDE_IN_SCHEMA)

    return SchedulerConfig.model_validate(config)
