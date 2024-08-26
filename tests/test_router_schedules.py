"""Test Scheduler API Router."""

from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.interval import IntervalTrigger as APSIntervalTrigger
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.schemas import (
    CalendarIntervalTrigger,
    CronTrigger,
    IntervalTrigger,
    Schedule,
    UnknownTrigger,
)
from pydantic import TypeAdapter
from typer import echo


def echo_test1() -> None:
    """Test function 1."""
    echo("test")


def echo_test2() -> None:
    """Test function 2."""
    echo("test2")


def echo_test3() -> None:
    """Test function 3."""
    echo("test3")


def echo_test4() -> None:
    """Test function 4."""
    echo("test4")


def test_schedules_api_router() -> None:
    """Test schedules API router."""
    # Arrange
    scheduler_app = SchedulerApp()
    scheduler_app.interval(hours=1)(echo_test1)
    scheduler_app.cron(day_of_week=1)(echo_test2)
    scheduler_app.calendar_interval(days=1)(echo_test3)
    unknown_trigger = OrTrigger([APSIntervalTrigger(seconds=1), APSIntervalTrigger(minutes=1)])
    scheduler_app.schedules.append((echo_test4, unknown_trigger))
    expected_schedules_count = 4

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(scheduler_app.api.prefix + "/schedules")
    response.raise_for_status()
    schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(schedules) == expected_schedules_count

    interval_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "IntervalTrigger")
    assert interval_schedule.id == "auto:tests.test_router_schedules:echo_test1"
    assert interval_schedule.task_id == "tests.test_router_schedules:echo_test1"
    assert isinstance(interval_schedule.trigger, IntervalTrigger)
    assert interval_schedule.trigger.hours == 1

    cron_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "CronTrigger")
    assert cron_schedule.id == "auto:tests.test_router_schedules:echo_test2"
    assert cron_schedule.task_id == "tests.test_router_schedules:echo_test2"
    assert isinstance(cron_schedule.trigger, CronTrigger)
    assert cron_schedule.trigger.day_of_week == 1

    calendar_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "CalendarIntervalTrigger")
    assert calendar_schedule.id == "auto:tests.test_router_schedules:echo_test3"
    assert calendar_schedule.task_id == "tests.test_router_schedules:echo_test3"
    assert isinstance(calendar_schedule.trigger, CalendarIntervalTrigger)
    assert calendar_schedule.trigger.days == 1

    unknown_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "UnknownTrigger")
    assert unknown_schedule.id == "auto:tests.test_router_schedules:echo_test4"
    assert unknown_schedule.task_id == "tests.test_router_schedules:echo_test4"
    assert isinstance(unknown_schedule.trigger, UnknownTrigger)
