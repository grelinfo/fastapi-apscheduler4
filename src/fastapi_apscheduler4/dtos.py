"""Data Transfer Objects (DTOs)."""

from typing import Protocol

from apscheduler.abc import Trigger as APSchedulerTrigger
from pydantic import BaseModel, Field


class NamedCallable(Protocol):
    """Protocol for a callable with a __name__ attribute (e.g., functions)."""

    __name__: str

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Call the function."""
        ...


ScheduleType = tuple[NamedCallable, APSchedulerTrigger]


class LimitOffset(BaseModel):
    """Limit Offset."""

    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
