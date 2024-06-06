"""Scheduler."""

from __future__ import annotations

from typing import TYPE_CHECKING, ParamSpec, TypeVar

from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from fastapi_apscheduler4.errors import ScheduleAlreadyExistsError

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Self

    from fastapi_apscheduler4.dtos import ScheduleType

P = ParamSpec("P")
RT = TypeVar("RT")


class Scheduler:
    """Scheduler.

    Provides decorators to schedule tasks.
    """

    def __init__(self) -> None:
        """Initialize the scheduler.

        Args:
            app: FastAPI application.
        """
        self._schedules: list[ScheduleType] = []

    def include(self, scheduler: Self) -> None:
        """Include the scheduler."""
        self._schedules.extend(scheduler.schedules)

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

        def decorator(func: Callable[P, RT]) -> Callable[P, RT]:
            self.add_schedule(
                func,
                IntervalTrigger(
                    weeks=weeks,
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    microseconds=microseconds,
                ),
            )
            return func

        return decorator

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

        def decorator(func: Callable[P, RT]) -> Callable[P, RT]:
            self.add_schedule(
                func,
                CronTrigger(
                    year=year,
                    month=month,
                    day=day,
                    week=week,
                    day_of_week=day_of_week,
                    hour=hour,
                    minute=minute,
                    second=second,
                ),
            )

            return func

        return decorator

    def calendar_interval(  # noqa: PLR0913
        self,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> Callable[[Callable[P, RT]], Callable[P, RT]]:
        """Decorator to schedule a task on calendar-based intervals, at a specific time of day.

        See: https://apscheduler.readthedocs.io/en/master/api.html#apscheduler.triggers.calendarinterval.CalendarIntervalTrigger
        """

        def decorator(func: Callable[P, RT]) -> Callable[P, RT]:
            self.add_schedule(
                func,
                CalendarIntervalTrigger(
                    years=years,
                    months=months,
                    weeks=weeks,
                    days=days,
                    hour=hour,
                    minute=minute,
                    second=second,
                ),
            )
            return func

        return decorator

    @property
    def schedules(self) -> list[ScheduleType]:
        """Get the schedules."""
        return self._schedules

    def add_schedule(
        self,
        func: Callable[P, RT],
        trigger: IntervalTrigger | CronTrigger | CalendarIntervalTrigger,
    ) -> None:
        """Add a schedule."""
        already_exists = any(func == schedule[0] for schedule in self._schedules)
        if already_exists:
            raise ScheduleAlreadyExistsError(func)
        self._schedules.append((func, trigger))
