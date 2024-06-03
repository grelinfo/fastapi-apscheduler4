"""Scheduler Schemas.

The data structures are almost the same as the APSchedulers translated to pydantic with some readability improvements.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, Discriminator, Tag

from fastapi_apscheduler4.utils import enforce_enum_name, transform_tzinfo_to_str

SCHEDULE_PREFIX = "auto:"

TimezoneFromTzinfo = Annotated[str, BeforeValidator(transform_tzinfo_to_str)]
"""Timezone in string format."""


class CoalescePolicy(str, Enum):
    """Coalesce Policy."""

    EARLIEST = "earliest"
    LATEST = "latest"
    ALL = "all"


class TriggerType(str, Enum):
    """Trigger Type."""

    INTERVAL = "IntervalTrigger"
    CRON = "CronTrigger"
    CALENDAR_INTERVAL = "CalendarIntervalTrigger"
    UNKNOWN = "UnknownTrigger"


def model_trigger_discriminator(v: Any) -> str:  # noqa: ANN401
    """Model Trigger Discriminator."""
    type_ = v.get("type", None) if isinstance(v, dict) else v.__class__.__name__

    if type_ in (TriggerType.INTERVAL.value, TriggerType.CRON.value, TriggerType.CALENDAR_INTERVAL.value):
        return TriggerType(type_).value

    return TriggerType.UNKNOWN.value


class BaseTrigger(BaseModel):
    """Base Trigger."""

    type: TriggerType


class UnknownTrigger(BaseTrigger):
    """Unknown Trigger.

    The unknown trigger is used when the trigger type is not recognized to avoid crashes.
    """

    type: Literal[TriggerType.UNKNOWN] = TriggerType.UNKNOWN


class CalendarIntervalTrigger(BaseTrigger):
    """Calendar Interval Trigger."""

    type: Literal[TriggerType.CALENDAR_INTERVAL] = TriggerType.CALENDAR_INTERVAL
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hour: int = 0
    minute: int = 0
    second: int = 0
    start_date: date
    end_date: date | None = None
    timezone: TimezoneFromTzinfo


class IntervalTrigger(BaseTrigger):
    """Interval Trigger."""

    type: Literal[TriggerType.INTERVAL] = TriggerType.INTERVAL
    weeks: float = 0
    days: float = 0
    hours: float = 0
    minutes: float = 0
    seconds: float = 0
    microseconds: float = 0
    start_time: datetime


class CronTrigger(BaseTrigger):
    """Cron Trigger."""

    type: Literal[TriggerType.CRON] = TriggerType.CRON
    year: int | str | None = None
    month: int | str | None = None
    day: int | str | None = None
    week: int | str | None = None
    day_of_week: int | str | None = None
    hour: int | str | None = None
    minute: int | str | None = None
    second: int | str | None = None
    start_time: datetime
    end_time: datetime | None = None
    timezone: TimezoneFromTzinfo


class Schedule(BaseModel):
    """Schedule."""

    id: str
    task_id: str
    trigger: Annotated[
        Annotated[IntervalTrigger, Tag(TriggerType.INTERVAL)]
        | Annotated[CronTrigger, Tag("CronTrigger")]
        | Annotated[CalendarIntervalTrigger, Tag(TriggerType.CALENDAR_INTERVAL)]
        | Annotated[UnknownTrigger, Tag(TriggerType.UNKNOWN)],
        Discriminator(model_trigger_discriminator),
    ]

    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None
    coalesce: Annotated[CoalescePolicy, BeforeValidator(enforce_enum_name)]
    misfire_grace_time: timedelta | None = None
    max_jitter: timedelta | None = None
    next_fire_time: datetime | None = None
    last_fire_time: datetime | None = None
    acquired_by: str | None = None
    acquired_until: datetime | None = None


class Task(BaseModel):
    """Task."""

    id: str
    func: str | None = None
    job_executor: str
    max_running_jobs: int | None = None
    misfire_grace_time: timedelta | None = None
