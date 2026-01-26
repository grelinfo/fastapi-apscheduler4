"""End-to-end workflow tests."""

import asyncio
from datetime import datetime

import pytest
from apscheduler import RunState
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.schemas import Schedule, Task

# Global counter for task execution tracking
execution_counter: dict[str, int] = {}


def increment_counter(task_name: str) -> None:
    """Increment execution counter for a task."""
    execution_counter[task_name] = execution_counter.get(task_name, 0) + 1


# Module-level task functions (required by APScheduler)
def integration_task_a() -> None:
    """Integration test task A."""
    increment_counter("task_a")


def integration_task_b() -> None:
    """Integration test task B."""
    increment_counter("task_b")


def integration_task_c() -> None:
    """Integration test task C."""
    increment_counter("task_c")


@pytest.fixture
def scheduler_app_with_two_tasks(scheduler_app: SchedulerApp) -> SchedulerApp:
    """Scheduler app with two tasks for integration testing."""
    scheduler_app.interval(seconds=0.1)(integration_task_a)
    scheduler_app.interval(seconds=0.15)(integration_task_b)
    return scheduler_app


@pytest.fixture
def scheduler_app_with_three_tasks(scheduler_app: SchedulerApp) -> SchedulerApp:
    """Scheduler app with three tasks using different triggers."""
    scheduler_app.interval(hours=1)(integration_task_a)
    scheduler_app.cron(hour=0)(integration_task_b)
    scheduler_app.calendar_interval(days=1)(integration_task_c)
    return scheduler_app


@pytest.mark.e2e
def test_full_lifecycle_workflow(scheduler_app_with_two_tasks: SchedulerApp) -> None:
    """Test full application lifecycle with scheduler and API."""
    # Arrange
    execution_counter.clear()
    app = FastAPI(lifespan=scheduler_app_with_two_tasks.lifespan)
    scheduler_app_with_two_tasks.setup(app)
    expected_schedules_count = 2
    expected_tasks_count = 2

    # Act & Assert
    with TestClient(app) as client:
        # Verify scheduler is running
        assert scheduler_app_with_two_tasks.apscheduler.state == RunState.started

        # Check schedules endpoint
        response = client.get(f"{scheduler_app_with_two_tasks.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

        assert response.status_code == status.HTTP_200_OK
        assert len(schedules) == expected_schedules_count

        # Check tasks endpoint
        response = client.get(f"{scheduler_app_with_two_tasks.api.prefix}/tasks")
        tasks = TypeAdapter(list[Task]).validate_json(response.text)

        assert response.status_code == status.HTTP_200_OK
        assert len(tasks) == expected_tasks_count

        # Let tasks execute
        asyncio.run(asyncio.sleep(0.5))

        # Verify tasks executed
        assert execution_counter.get("task_a", 0) > 0
        assert execution_counter.get("task_b", 0) > 0

    # Verify scheduler stopped after context exit
    assert scheduler_app_with_two_tasks.apscheduler.state == RunState.stopped


@pytest.mark.e2e
def test_schedule_crud_workflow(scheduler_app: SchedulerApp) -> None:
    """Test complete CRUD workflow for schedules through our API."""
    # Arrange
    scheduler_app.interval(hours=1)(integration_task_a)
    scheduler_app.interval(hours=2)(integration_task_b)
    expected_schedules_count = 2
    expected_schedules_count_after_delete = 1

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act & Assert
    with TestClient(app) as client:
        # Create (via decorator, already done)
        # Read - List all schedules
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)

        assert response.status_code == status.HTTP_200_OK
        assert len(schedules) == expected_schedules_count

        schedule_id = schedules[0].id

        # Read - Get specific schedule
        response = client.get(f"{scheduler_app.api.prefix}/schedules/{schedule_id}")
        schedule = Schedule.model_validate_json(response.text)

        assert response.status_code == status.HTTP_200_OK
        assert schedule.id == schedule_id

        # Delete - Attempt without force (should fail for auto schedule)
        response = client.delete(f"{scheduler_app.api.prefix}/schedules/{schedule_id}")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Delete - With force
        response = client.delete(f"{scheduler_app.api.prefix}/schedules/{schedule_id}?force=true")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)
        assert len(schedules) == expected_schedules_count_after_delete


@pytest.mark.e2e
def test_task_retrieval_workflow(scheduler_app_with_three_tasks: SchedulerApp) -> None:
    """Test task retrieval workflow through API after registration."""
    # Arrange
    app = FastAPI(lifespan=scheduler_app_with_three_tasks.lifespan)
    scheduler_app_with_three_tasks.setup(app)
    expected_tasks_count = 3
    task_id_prefix = "tests.e2e.test_workflows:integration_task"

    # Act
    with TestClient(app) as client:
        # Get all tasks
        response = client.get(f"{scheduler_app_with_three_tasks.api.prefix}/tasks")
        tasks = TypeAdapter(list[Task]).validate_json(response.text)

        # Get specific task (using first task from list)
        specific_task_id = tasks[0].id
        specific_response = client.get(f"{scheduler_app_with_three_tasks.api.prefix}/tasks/{specific_task_id}")
        task = Task.model_validate_json(specific_response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(tasks) == expected_tasks_count

    assert specific_response.status_code == status.HTTP_200_OK
    assert task.id.startswith(task_id_prefix)
    assert task.job_executor == "async"


@pytest.mark.e2e
def test_pagination_workflow(scheduler_app_with_three_tasks: SchedulerApp) -> None:
    """Test pagination workflow across tasks and schedules."""
    # Arrange
    app = FastAPI(lifespan=scheduler_app_with_three_tasks.lifespan)
    scheduler_app_with_three_tasks.setup(app)
    expected_total_count = "3"
    expected_first_page_count = 2
    expected_second_page_count = 1

    # Act
    with TestClient(app) as client:
        # Test schedules pagination - first page
        schedules_page1_response = client.get(f"{scheduler_app_with_three_tasks.api.prefix}/schedules?limit=2&offset=0")
        schedules_page1 = TypeAdapter(list[Schedule]).validate_json(schedules_page1_response.text)

        # Test schedules pagination - second page
        schedules_page2_response = client.get(f"{scheduler_app_with_three_tasks.api.prefix}/schedules?limit=2&offset=2")
        schedules_page2 = TypeAdapter(list[Schedule]).validate_json(schedules_page2_response.text)

        # Test tasks pagination
        tasks_response = client.get(f"{scheduler_app_with_three_tasks.api.prefix}/tasks?limit=1&offset=0")
        tasks = TypeAdapter(list[Task]).validate_json(tasks_response.text)

    # Assert
    assert schedules_page1_response.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert schedules_page1_response.headers["X-Total-Count"] == expected_total_count
    assert len(schedules_page1) == expected_first_page_count

    assert schedules_page2_response.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert len(schedules_page2) == expected_second_page_count

    assert tasks_response.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert tasks_response.headers["X-Total-Count"] == expected_total_count
    assert len(tasks) == expected_second_page_count


@pytest.mark.e2e
def test_error_handling_workflow(scheduler_app: SchedulerApp) -> None:
    """Test error handling workflow across the system."""
    # Arrange
    scheduler_app.interval(hours=1)(integration_task_a)
    non_existent_id = "non-existent"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        # Test 404 for non-existent schedule
        schedule_not_found_response = client.get(f"{scheduler_app.api.prefix}/schedules/{non_existent_id}")

        # Test 404 for non-existent task
        task_not_found_response = client.get(f"{scheduler_app.api.prefix}/tasks/{non_existent_id}")

        # Test 404 when deleting non-existent schedule
        delete_not_found_response = client.delete(f"{scheduler_app.api.prefix}/schedules/{non_existent_id}")

        # Test 405 when deleting auto schedule without force
        schedules_response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(schedules_response.text)
        schedule_id = schedules[0].id

        delete_without_force_response = client.delete(f"{scheduler_app.api.prefix}/schedules/{schedule_id}")

    # Assert
    assert schedule_not_found_response.status_code == status.HTTP_404_NOT_FOUND
    assert task_not_found_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_not_found_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_without_force_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.e2e
def test_api_response_format_workflow(scheduler_app: SchedulerApp) -> None:
    """Test that API responses contain proper metadata through a complete workflow."""
    # Arrange
    scheduler_app.interval(hours=1)(integration_task_a)
    expected_task_id_prefix = "tests.e2e.test_workflows:integration_task"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/schedules")
        schedules = TypeAdapter(list[Schedule]).validate_json(response.text)
        schedule = schedules[0]

    # Assert - Verify our API serialization works correctly
    assert schedule.id.startswith("auto:")
    assert schedule.task_id.startswith(expected_task_id_prefix)
    assert schedule.trigger.type == "IntervalTrigger"
    assert isinstance(schedule.next_fire_time, datetime)
    assert schedule.next_fire_time.tzinfo is not None
