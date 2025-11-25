"""Scheduler setup."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Annotated, Any, ParamSpec

from apscheduler import AsyncScheduler, ConflictPolicy
from apscheduler._marshalling import callable_to_ref
from typing_extensions import Doc, TypeVar

from fastapi_apscheduler4 import logger
from fastapi_apscheduler4.apscheduler_builder import APSSchedulerBuilder
from fastapi_apscheduler4.config import (
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
    SchedulerAPIConfig,
    SchedulerAPIEnvConfig,
    SchedulerConfig,
    SchedulerEnvConfig,
)
from fastapi_apscheduler4.errors import AlreadySetupError
from fastapi_apscheduler4.scheduler import Scheduler
from fastapi_apscheduler4.schemas import SCHEDULE_PREFIX

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from fastapi import FastAPI

P = ParamSpec("P")
RT = TypeVar("RT")


class SchedulerApp(Scheduler):
    """FastAPI-APScheduler4 App."""

    def __init__(
        self,
        *,
        scheduler: Annotated[
            SchedulerConfig | None,
            Doc(
                """
                Scheduler Configuration.

                If not provided, it will be created from environment variables.
                """
            ),
        ] = None,
        api: Annotated[
            SchedulerAPIConfig | None,
            Doc(
                """
                API Configuration.

                If not provided, it will be created from environment variables.
                """
            ),
        ] = None,
        postgres: Annotated[
            PostgresConfig | None,
            Doc(
                """
                Postgres config.

                If not provided, it will be created from environment variables.
                """
            ),
        ] = None,
        redis: Annotated[
            RedisConfig | None,
            Doc(
                """
                Redis explicit config.

                If not provided, it will be created from environment variables.
                """
            ),
        ] = None,
        _apscheduler: Annotated[
            AsyncScheduler | None,
            Doc(
                """
                APScheduler custom instance if you have specific needs.

                All other config will be ignored without any warning or error.
                Please open a feature request if you need something specific.
                """
            ),
        ] = None,
    ) -> None:
        """Initialize the plugin.

        Raises:
            ConfigNotFoundError: If required config is not provided.
        """
        super().__init__()
        self._scheduler = scheduler or SchedulerEnvConfig()
        self._api = api or SchedulerAPIEnvConfig()
        if _apscheduler:
            self._apscheduler = _apscheduler
            self._event_broker = None
            self._data_store = None
        else:
            apscheduler_builder = APSSchedulerBuilder(scheduler=self._scheduler, postgres=postgres, redis=redis)
            self._apscheduler = apscheduler_builder.build()
            self._event_broker = apscheduler_builder.computed_event_broker_type
            self._data_store = apscheduler_builder.computed_data_store_type

    def setup(self, app: FastAPI) -> None:
        """Initialize the plugin."""
        if app.extra.get("apscheduler"):
            raise AlreadySetupError

        app.extra["apscheduler"] = self.apscheduler

        if self.api.enabled:
            from fastapi_apscheduler4.routers.schedules import SchedulesAPIRouter
            from fastapi_apscheduler4.routers.tasks import TasksAPIRouter

            app.include_router(SchedulesAPIRouter.from_config(self.apscheduler, self.api))
            app.include_router(TasksAPIRouter.from_config(self.apscheduler, self.api))

    @property
    def scheduler(self) -> SchedulerConfig:
        """Get the scheduler configuration."""
        return self._scheduler

    @property
    def api(self) -> SchedulerAPIConfig:
        """Get the API configuration."""
        return self._api

    @property
    def apscheduler(self) -> AsyncScheduler:
        """Get the APScheduler."""
        return self._apscheduler

    @property
    def event_broker(self) -> EventBrokerType | None:
        """Get the event broker."""
        return self._event_broker

    @property
    def data_store(self) -> DataStoreType | None:
        """Get the data store."""
        return self._data_store

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG002
        """Start the scheduler."""
        async with self.apscheduler:
            await self._clean_auto_schedules()
            await self._add_auto_schedules()
            if self.scheduler.auto_start:
                await self.apscheduler.start_in_background()
            yield

    async def _add_auto_schedules(self) -> None:
        """Add auto schedules."""
        for func, trigger in self.schedules:
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
        configured_schedule_ids = {self._get_schedule_id(func) for func, _ in self.schedules}
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
