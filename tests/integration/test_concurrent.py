"""Test concurrent operations."""

import asyncio
import sys

import pytest
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.schemas import Schedule


# Module-level task functions (required by APScheduler)
def concurrent_task1() -> None:
    """First concurrent test task."""


def concurrent_task2() -> None:
    """Second concurrent test task."""


def concurrent_task3() -> None:
    """Third concurrent test task."""


def concurrent_task4() -> None:
    """Fourth concurrent test task."""


def concurrent_task5() -> None:
    """Fifth concurrent test task."""


@pytest.mark.anyio
async def test_concurrent_schedule_registration(scheduler_app: SchedulerApp) -> None:
    """Test concurrent schedule registration."""
    # Arrange
    trigger = IntervalTrigger(hours=1)
    tasks = [concurrent_task1, concurrent_task2, concurrent_task3, concurrent_task4, concurrent_task5]
    expected_schedules_count = 5

    # Act
    async with scheduler_app.apscheduler:
        if sys.version_info >= (3, 11):
            async with asyncio.TaskGroup() as tg:
                for task in tasks:
                    tg.create_task(scheduler_app.apscheduler.add_schedule(task, trigger=trigger))
        else:
            await asyncio.gather(*[scheduler_app.apscheduler.add_schedule(task, trigger=trigger) for task in tasks])

        schedules = await scheduler_app.apscheduler.get_schedules()

    # Assert
    assert len(schedules) == expected_schedules_count

    schedule_task_ids = {schedule.task_id for schedule in schedules}
    assert all(tid.startswith("tests.integration.test_concurrent:concurrent_task") for tid in schedule_task_ids)


@pytest.mark.integration
def test_concurrent_schedule_registration_via_decorators(scheduler_app: SchedulerApp) -> None:
    """Test that multiple decorators can register schedules without conflicts."""
    # Arrange
    scheduler_app.interval(hours=1)(concurrent_task1)
    scheduler_app.interval(hours=2)(concurrent_task2)
    scheduler_app.cron(hour=0)(concurrent_task3)
    scheduler_app.calendar_interval(days=1)(concurrent_task4)
    scheduler_app.interval(minutes=30)(concurrent_task5)
    expected_schedules_count = 5

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(schedules) == expected_schedules_count

    schedule_task_ids = {schedule.task_id for schedule in schedules}
    assert all(tid.startswith("tests.integration.test_concurrent:concurrent_task") for tid in schedule_task_ids)


@pytest.mark.anyio
async def test_concurrent_api_requests(scheduler_app: SchedulerApp) -> None:
    """Test concurrent API requests don't cause race conditions."""
    # Arrange
    scheduler_app.interval(hours=1)(concurrent_task1)
    scheduler_app.interval(hours=2)(concurrent_task2)
    scheduler_app.interval(hours=3)(concurrent_task3)
    expected_status_code = 200

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        api_tasks = [
            asyncio.to_thread(client.get, f"{scheduler_app.api.prefix}/schedules"),
            asyncio.to_thread(client.get, f"{scheduler_app.api.prefix}/tasks"),
            asyncio.to_thread(client.get, f"{scheduler_app.api.prefix}/schedules"),
            asyncio.to_thread(client.get, f"{scheduler_app.api.prefix}/tasks"),
        ]
        if sys.version_info >= (3, 11):
            async with asyncio.TaskGroup() as tg:
                results = [tg.create_task(task) for task in api_tasks]

            # Assert
            for result in results:
                assert result.result().status_code == expected_status_code
        else:
            results = await asyncio.gather(*api_tasks)

            # Assert
            for result in results:
                assert result.status_code == expected_status_code
