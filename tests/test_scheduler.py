"""Test Scheduler."""

import pytest
from apscheduler.triggers.interval import IntervalTrigger as APSIntervalTrigger

from fastapi_apscheduler4.errors import ScheduleAlreadyExistsError
from fastapi_apscheduler4.scheduler import Scheduler


def test_interval_decorator() -> None:
    """Test interval decorator."""
    # Arrange
    scheduler = Scheduler()
    schedules_count = 2

    # Act
    @scheduler.interval(seconds=1)
    def every_second() -> None:
        """Test register every second."""

    @scheduler.interval(minutes=1)
    async def every_minute() -> None:
        """Test register async every minute."""

    # Assert
    assert len(scheduler._schedules) == schedules_count
    scheduler1_func, scheduler1_trigger = scheduler._schedules[0]
    scheduler2_func, scheduler2_trigger = scheduler._schedules[1]

    assert scheduler1_func == every_second
    assert isinstance(scheduler1_trigger, APSIntervalTrigger)
    assert scheduler1_trigger.seconds == 1
    assert scheduler1_trigger.minutes == 0

    assert scheduler2_func == every_minute
    assert isinstance(scheduler2_trigger, APSIntervalTrigger)
    assert scheduler2_trigger.seconds == 0
    assert scheduler2_trigger.minutes == 1


def test_interval_decorator_multiple_error() -> None:
    """Test multiple decorators on the same function."""
    # Arrange
    scheduler = Scheduler()

    # Act
    # Order of decorators are bottom to top (inner to outer)
    with pytest.raises(ScheduleAlreadyExistsError):

        @scheduler.interval(minutes=1)
        @scheduler.interval(seconds=1)
        def mutiple_interval() -> None:
            """Test register every second."""

    # Assert
    assert len(scheduler._schedules) == 1
    scheduler1_func, scheduler1_trigger = scheduler._schedules[0]

    assert hasattr(scheduler1_func, "__name__")
    assert scheduler1_func.__name__ == "mutiple_interval"
    assert isinstance(scheduler1_trigger, APSIntervalTrigger)
    assert scheduler1_trigger.seconds == 1
    assert scheduler1_trigger.minutes == 0
