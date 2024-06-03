"""Data Transfer Objects (DTOs)."""

from collections.abc import Callable
from typing import Any

from apscheduler.abc import Trigger as APSchedulerTrigger
from pydantic import BaseModel, Field

ScheduleType = tuple[Callable[..., Any], APSchedulerTrigger]


class LimitOffset(BaseModel):
    """Limit Offset."""

    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
