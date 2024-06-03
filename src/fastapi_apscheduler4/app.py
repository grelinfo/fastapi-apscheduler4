"""Scheduler setup."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from apscheduler import AsyncScheduler, ConflictPolicy
from apscheduler._marshalling import callable_to_ref
from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from typing_extensions import assert_never

from fastapi_apscheduler4 import logger
from fastapi_apscheduler4.config import (
    APSchedulerConfig,
    DataStoreType,
    EventBrokerType,
    SchedulerConfig,
)
from fastapi_apscheduler4.errors import AlreadySetupError, MissingConfigError, MissingEngineError
from fastapi_apscheduler4.scheduler import Scheduler
from fastapi_apscheduler4.schemas import SCHEDULE_PREFIX
from fastapi_apscheduler4.settings import create_config_from_env_vars

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from apscheduler.abc import DataStore, EventBroker
    from fastapi import FastAPI


class SchedulerApp:
    """FastAPI-APScheduler4 App."""

    def __init__(self, config: SchedulerConfig | None = None) -> None:
        """Initialize the plugin."""
        super().__init__()
        self.config: SchedulerConfig = config or create_config_from_env_vars()
        self.scheduler = Scheduler()
        self.engine: AsyncEngine | None = self._create_engine(self.config)
        self.apscheduler: AsyncScheduler = self._create_apscheduler(self.config.apscheduler)

    def setup(self, app: FastAPI) -> None:
        """Initialize the plugin."""
        if app.extra.get("apscheduler"):
            raise AlreadySetupError

        app.extra["apscheduler"] = self.apscheduler

        if self.config.api:
            from fastapi_apscheduler4.routers.schedules import SchedulesAPIRouter
            from fastapi_apscheduler4.routers.tasks import TasksAPIRouter

            app.include_router(SchedulesAPIRouter.from_config(self.apscheduler, self.config.api))
            app.include_router(TasksAPIRouter.from_config(self.apscheduler, self.config.api))

    def include_scheduler(self, scheduler: Scheduler) -> None:
        """Include the scheduler."""
        self.scheduler.include_scheduler(scheduler)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG002
        """Start the scheduler."""
        async with self.apscheduler:
            await self._clean_auto_schedules()
            await self._add_auto_schedules()
            await self.apscheduler.start_in_background()
            yield

    async def _add_auto_schedules(self) -> None:
        """Add auto schedules."""
        for func, trigger in self.scheduler.schedules:
            schedule_id = self._get_schedule_id(func)
            logger.debug(f"Scheduler: Configure schedule {schedule_id}")
            await self.apscheduler.add_schedule(
                func,
                id=schedule_id,
                trigger=trigger,
                conflict_policy=ConflictPolicy.replace,
            )

    async def _clean_auto_schedules(self) -> None:
        """Clean unconfigured schedules."""
        configured_schedule_ids = {self._get_schedule_id(func) for func, _ in self.scheduler.schedules}
        active_auto_schedule_ids = {
            schedule.id
            for schedule in await self.apscheduler.get_schedules()
            if schedule.id.startswith(SCHEDULE_PREFIX)
        }

        for schedule_id in active_auto_schedule_ids - configured_schedule_ids:
            logger.warning(f"Scheduler: Remove schedule {schedule_id}")
            await self.apscheduler.remove_schedule(schedule_id)

    def _get_schedule_id(self, func: Callable[..., Any]) -> str:
        """Get the schedule ID."""
        return SCHEDULE_PREFIX + callable_to_ref(func)

    @staticmethod
    def _create_engine(config: SchedulerConfig) -> AsyncEngine | None:
        """Create the engine."""
        if isinstance(config.apscheduler, AsyncScheduler):
            return None

        if (
            config.apscheduler.computed_data_store is not DataStoreType.POSTGRES
            and config.apscheduler.event_broker is not EventBrokerType.POSTGRES
        ):
            return None

        if not config.apscheduler.postgres:
            raise MissingConfigError(
                "FastAPIAPScheduler4ConfigDict.postgres", "Must be set when using Postgres Store or Broker."
            )

        if isinstance(config.apscheduler.postgres, AsyncEngine):
            return config.apscheduler.postgres

        # Lazy imports to avoid SQLAlchemy dependency
        from sqlalchemy.ext.asyncio import create_async_engine

        return create_async_engine(config.apscheduler.postgres.get_postgres_url())

    def _create_apscheduler(self, config: APSchedulerConfig | AsyncScheduler) -> AsyncScheduler:
        """Create APScheduler Scheduler."""
        if isinstance(config, AsyncScheduler):
            return config

        return AsyncScheduler(
            data_store=self._create_apscheduler_data_store(config),
            event_broker=self._create_apscheduler_event_broker(config),
        )

    def _create_apscheduler_data_store(self, config: APSchedulerConfig) -> DataStore:
        """Create APScheduler Data Store."""
        store = config.computed_data_store

        if store is DataStoreType.MEMORY:
            return MemoryDataStore()

        if store is DataStoreType.POSTGRES:
            # Lazy imports to avoid SQLAlchemy dependency
            from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore

            if not self.engine:
                raise MissingEngineError
            return SQLAlchemyDataStore(self.engine)

        assert_never(store)

    def _create_apscheduler_event_broker(self, config: APSchedulerConfig) -> EventBroker:
        """Get APScheduler Event Broker."""
        broker = config.computed_event_broker

        if broker is EventBrokerType.MEMORY:
            return LocalEventBroker()

        if broker is EventBrokerType.REDIS:
            # Lazy imports to avoid Redis dependency
            from apscheduler.eventbrokers.redis import RedisEventBroker

            if not config.redis:
                raise MissingConfigError("APSchedulerConfig.redis", "Must be set when using the Redis Event Broker.")

            if isinstance(config.redis, Redis):
                return RedisEventBroker(config.redis, channel=config.redis_channel)

            return RedisEventBroker(config.redis.get_redis_url(), channel=config.redis_channel)

        if broker is EventBrokerType.POSTGRES:
            # Lazy imports to avoid SQLAlchemy dependency
            from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

            if not self.engine:
                raise MissingEngineError
            return AsyncpgEventBroker.from_async_sqla_engine(self.engine)

        assert_never(broker)
