"""Test Scheduler API Router."""

# ruff: noqa: T201
import pytest
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.interval import IntervalTrigger as APSIntervalTrigger
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.schemas import (
    CalendarIntervalTrigger,
    CronTrigger,
    IntervalTrigger,
    Schedule,
    UnknownTrigger,
)


# Module-level task functions (required by APScheduler)
def schedule_task1() -> None:
    """First test task."""
    print("test1")


def schedule_task2() -> None:
    """Second test task."""
    print("test2")


def schedule_task3() -> None:
    """Third test task."""
    print("test3")


def schedule_task4() -> None:
    """Fourth test task."""
    print("test4")


@pytest.fixture
def scheduler_app_with_schedules(scheduler_app: SchedulerApp) -> SchedulerApp:
    """Scheduler app with multiple schedule types."""
    scheduler_app.interval(hours=1)(schedule_task1)
    scheduler_app.cron(day_of_week=1)(schedule_task2)
    scheduler_app.calendar_interval(days=1)(schedule_task3)
    unknown_trigger = OrTrigger([APSIntervalTrigger(seconds=1), APSIntervalTrigger(minutes=1)])
    scheduler_app.schedules.append((schedule_task4, unknown_trigger))
    return scheduler_app


@pytest.fixture
def client_with_schedules(scheduler_app_with_schedules: SchedulerApp) -> TestClient:
    """Test client with scheduler app that has schedules."""
    app = FastAPI(lifespan=scheduler_app_with_schedules.lifespan)
    scheduler_app_with_schedules.setup(app)
    return TestClient(app)


@pytest.mark.integration
def test_schedules_api_router(scheduler_app_with_schedules: SchedulerApp, client_with_schedules: TestClient) -> None:
    """Test schedules API router."""
    # Arrange
    expected_schedules_count = 4
    api_prefix = scheduler_app_with_schedules.api.prefix

    # Act
    with client_with_schedules as client:
        response = client.get(f"{api_prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(schedules) == expected_schedules_count

    interval_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "IntervalTrigger")
    assert interval_schedule.id.startswith("auto:tests.integration.test_router_schedules:schedule_task")
    assert interval_schedule.task_id.startswith("tests.integration.test_router_schedules:schedule_task")
    assert isinstance(interval_schedule.trigger, IntervalTrigger)
    assert interval_schedule.trigger.hours == 1

    cron_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "CronTrigger")
    assert cron_schedule.id.startswith("auto:tests.integration.test_router_schedules:schedule_task")
    assert cron_schedule.task_id.startswith("tests.integration.test_router_schedules:schedule_task")
    assert isinstance(cron_schedule.trigger, CronTrigger)
    assert cron_schedule.trigger.day_of_week == 1

    calendar_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "CalendarIntervalTrigger")
    assert calendar_schedule.id.startswith("auto:tests.integration.test_router_schedules:schedule_task")
    assert calendar_schedule.task_id.startswith("tests.integration.test_router_schedules:schedule_task")
    assert isinstance(calendar_schedule.trigger, CalendarIntervalTrigger)
    assert calendar_schedule.trigger.days == 1

    unknown_schedule = next(schedule for schedule in schedules if schedule.trigger.type == "UnknownTrigger")
    assert unknown_schedule.id.startswith("auto:tests.integration.test_router_schedules:schedule_task")
    assert unknown_schedule.task_id.startswith("tests.integration.test_router_schedules:schedule_task")
    assert isinstance(unknown_schedule.trigger, UnknownTrigger)


@pytest.mark.integration
def test_get_schedule(scheduler_app: SchedulerApp) -> None:
    """Test get schedule by ID endpoint."""
    # Arrange
    scheduler_app.interval(hours=1)(schedule_task1)
    schedule_id = "auto:tests.integration.test_router_schedules:schedule_task1"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/schedules/{schedule_id}")
        schedule = Schedule.model_validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert schedule.id == schedule_id
    assert schedule.task_id == "tests.integration.test_router_schedules:schedule_task1"
    assert isinstance(schedule.trigger, IntervalTrigger)


@pytest.mark.integration
def test_get_schedule_not_found(scheduler_app: SchedulerApp) -> None:
    """Test get schedule returns 404 for non-existent schedule."""
    # Arrange
    scheduler_app.interval(hours=1)(schedule_task1)
    non_existent_schedule_id = "non-existent-schedule"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/schedules/{non_existent_schedule_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_delete_schedule(scheduler_app: SchedulerApp) -> None:
    """Test delete schedule endpoint without force returns 405."""
    # Arrange
    scheduler_app.interval(hours=1)(schedule_task1)

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)
    expected_schedules_count_initial = 1
    expected_schedules_count_after = 1

    # Act & Assert
    with TestClient(app) as client:
        # Verify schedule exists
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)
        assert len(schedules) == expected_schedules_count_initial

        # Attempt to delete without force
        schedule_id = schedules[0].id
        response = client.delete(f"{scheduler_app.api.prefix}/schedules/{schedule_id}")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Verify schedule still exists
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)
        assert len(schedules) == expected_schedules_count_after


@pytest.mark.integration
def test_delete_schedule_with_force(scheduler_app: SchedulerApp) -> None:
    """Test delete auto schedule with force=True."""
    # Arrange
    scheduler_app.interval(hours=1)(schedule_task1)

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)
    expected_schedules_count_after = 0

    # Act & Assert
    with TestClient(app) as client:
        # Get schedule ID
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)
        schedule_id = schedules[0].id

        # Delete with force=True
        delete_response = client.delete(f"{scheduler_app.api.prefix}/schedules/{schedule_id}?force=true")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)
        assert len(schedules) == expected_schedules_count_after


@pytest.mark.integration
def test_delete_schedule_not_found(scheduler_app: SchedulerApp) -> None:
    """Test delete schedule returns 404 for non-existent schedule."""
    # Arrange
    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)
    non_existent_schedule_id = "non-existent-schedule"

    # Act
    with TestClient(app) as client:
        response = client.delete(f"{scheduler_app.api.prefix}/schedules/{non_existent_schedule_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_list_schedules_pagination(scheduler_app: SchedulerApp) -> None:
    """Test list schedules with pagination."""
    # Arrange
    scheduler_app.interval(hours=1)(schedule_task1)
    scheduler_app.interval(hours=2)(schedule_task2)
    expected_limit = 1
    expected_total_count = "2"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/schedules?limit={expected_limit}&offset=0")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert response.headers["X-Total-Count"] == expected_total_count
    assert len(schedules) == expected_limit


@pytest.mark.integration
def test_list_schedules_empty(scheduler_app: SchedulerApp) -> None:
    """Test list schedules when no schedules are registered."""
    # Arrange
    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(schedules) == 0
