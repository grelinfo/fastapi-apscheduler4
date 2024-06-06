"""Scheduler setup."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Annotated, Any, ParamSpec, cast

from apscheduler import AsyncScheduler, ConflictPolicy
from apscheduler._marshalling import callable_to_ref
from typing_extensions import Doc, TypeVar, assert_never

from fastapi_apscheduler4 import logger
from fastapi_apscheduler4.config import (
    APSchedulerConfig,
    DataStoreType,
    EventBrokerType,
    RedisConfig,
    SchedulerConfig,
)
from fastapi_apscheduler4.errors import AlreadySetupError, InvalidConfigError
from fastapi_apscheduler4.scheduler import Scheduler
from fastapi_apscheduler4.schemas import SCHEDULE_PREFIX
from fastapi_apscheduler4.settings import get_config_from_env_vars

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from apscheduler.abc import DataStore, EventBroker
    from fastapi import FastAPI
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncEngine

P = ParamSpec("P")
RT = TypeVar("RT")


class SchedulerApp:
    """FastAPI-APScheduler4 App."""

    def __init__(
        self,
        config: Annotated[
            SchedulerConfig | None,
            Doc(
                """
            Scheduler Configuration.

            If not provided, the configuration will be created from the environment variables with `SchedulerSettings`.
            """
            ),
        ] = None,
        *,
        apscheduler: Annotated[
            AsyncScheduler | None,
            Doc(
                """
                APScheduler Async Scheduler.

                If not provided, a new scheduler will be created based on the config.
                """
            ),
        ] = None,
        engine: Annotated[
            AsyncEngine | None,
            Doc(
                """
                SQLAlchemy Async Engine.

                If not provided, a new engine could be created based on the config.
                """
            ),
        ] = None,
        redis: Annotated[
            Redis | None,
            Doc(
                """
                Redis Async Client.

                If not provided, a new client could be created based on the config.
                """
            ),
        ] = None,
    ) -> None:
        """Initialize the plugin."""
        self._config: SchedulerConfig = config or get_config_from_env_vars()
        self._scheduler: Scheduler = Scheduler()
        self._engine: AsyncEngine | None = engine
        self._redis: Redis | None = redis
        self._apscheduler: AsyncScheduler = apscheduler or self._create_apscheduler()

    def setup(self, app: FastAPI) -> None:
        """Initialize the plugin."""
        if app.extra.get("apscheduler"):
            raise AlreadySetupError

        app.extra["apscheduler"] = self.apscheduler

        if self._config.api.enabled:
            from fastapi_apscheduler4.routers.schedules import SchedulesAPIRouter
            from fastapi_apscheduler4.routers.tasks import TasksAPIRouter

            app.include_router(SchedulesAPIRouter.from_config(self.apscheduler, self._config.api))
            app.include_router(TasksAPIRouter.from_config(self.apscheduler, self._config.api))

    def include(self, scheduler: Scheduler) -> None:
        """Include the scheduler."""
        self._scheduler.include(scheduler)

    def interval(
        self,
        weeks: float = 0,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        microseconds: float = 0,
    ) -> Callable[[Callable[P, RT]], Callable[P, RT]]:
        """Decorator to schedule a task for a given interval.

        See: https://apscheduler.readthedocs.io/en/master/api.html#apscheduler.triggers.interval.IntervalTrigger
        """
        """Decorator to add an interval schedule."""
        return self._scheduler.interval(
            weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds
        )

    def cron(  # noqa: PLR0913
        self,
        year: int | str | None = None,
        month: int | str | None = None,
        day: int | str | None = None,
        week: int | str | None = None,
        day_of_week: int | str | None = None,
        hour: int | str | None = None,
        minute: int | str | None = None,
        second: int | str | None = None,
    ) -> Callable[[Callable[P, RT]], Callable[P, RT]]:
        """Decorator to schedule a task when current time matches all specified time constraints.

        See: https://apscheduler.readthedocs.io/en/master/api.html#apscheduler.triggers.cron.CronTrigger
        """
        return self._scheduler.cron(
            year=year,
            month=month,
            day=day,
            week=week,
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            second=second,
        )

    @property
    def apscheduler(self) -> AsyncScheduler:
        """Get the APScheduler."""
        return self._apscheduler

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
        for func, trigger in self._scheduler.schedules:
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
        configured_schedule_ids = {self._get_schedule_id(func) for func, _ in self._scheduler.schedules}
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

    def _create_engine(self, config: APSchedulerConfig | None) -> AsyncEngine:
        """Create the engine."""
        if not config or not config.postgres:
            raise InvalidConfigError("config.apscheduler.postgres", "Must be set when using Postgres Store or Broker.")

        # Lazy imports to avoid SQLAlchemy dependency
        from sqlalchemy.ext.asyncio import create_async_engine

        return create_async_engine(config.postgres.get_postgres_url())

    def _create_redis(self, config: APSchedulerConfig | None) -> Redis:
        """Create the Redis Client."""
        if not config or not isinstance(config.redis, RedisConfig):
            raise InvalidConfigError("config.apscheduler.redis", "Must be set when using Redis Broker.")

        # Lazy imports to avoid Redis dependency
        from redis.asyncio import Redis

        return cast(Redis, Redis.from_url(config.redis.get_redis_url()))  # mypy type inference issue

    def _create_apscheduler(self) -> AsyncScheduler:
        """Create APScheduler Async Scheduler."""
        return AsyncScheduler(
            self._create_apscheduler_data_store(self._config.apscheduler),
            self._create_apscheduler_event_broker(self._config.apscheduler),
        )

    def _create_apscheduler_data_store(self, config: APSchedulerConfig | None) -> DataStore:
        """Create APScheduler Data Store."""
        if self.data_store is DataStoreType.MEMORY:
            # Lazy imports to avoid useless dependencies
            from apscheduler.datastores.memory import MemoryDataStore

            return MemoryDataStore()

        if self.data_store is DataStoreType.POSTGRES:
            # Lazy imports to avoid SQLAlchemy dependency
            from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore

            self._engine = self._engine or self._create_engine(config)
            return SQLAlchemyDataStore(self._engine)

        assert_never(self.data_store)

    def _create_apscheduler_event_broker(self, config: APSchedulerConfig | None) -> EventBroker:
        """Get APScheduler Event Broker."""
        if self.event_broker is EventBrokerType.MEMORY:
            # Lazy imports to avoid useless dependencies
            from apscheduler.eventbrokers.local import LocalEventBroker

            return LocalEventBroker()

        if self.event_broker is EventBrokerType.REDIS:
            # Lazy imports to avoid Redis dependency
            from apscheduler.eventbrokers.redis import RedisEventBroker

            self._redis = self._redis or self._create_redis(config)

            if not config or not config.redis:
                raise InvalidConfigError("config.apscheduler.redis", "Must be set when using Redis Broker.")

            return RedisEventBroker(self._redis, channel=config.redis.channel)

        if self.event_broker is EventBrokerType.POSTGRES:
            # Lazy imports to avoid SQLAlchemy dependency
            from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

            self._engine = self._engine or self._create_engine(config)
            return AsyncpgEventBroker.from_async_sqla_engine(self._engine)

        assert_never(self.event_broker)

    @property
    def event_broker(self) -> EventBrokerType:
        """Event Broker.

        Priority:
        1. Explicit broker.
        2. Redis.
        3. Postgres.
        """
        if self._config.apscheduler and self._config.apscheduler.event_broker:
            return self._config.apscheduler.event_broker
        if self._redis:
            return EventBrokerType.REDIS
        if self._engine:
            return EventBrokerType.POSTGRES
        return EventBrokerType.MEMORY

    @property
    def data_store(self) -> DataStoreType:
        """Data Store.

        Priority:
        1. Explicit store.
        2. Postgres.
        3. Memory.
        """
        if self._config.apscheduler and self._config.apscheduler.data_store:
            return self._config.apscheduler.data_store
        if self._engine:
            return DataStoreType.POSTGRES
        return DataStoreType.MEMORY
