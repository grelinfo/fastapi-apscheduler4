"""Test Tasks API Router."""

# ruff: noqa: T201

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.schemas import Task


# Module-level task functions (required by APScheduler)
def task1() -> None:
    """First test task."""
    print("task1")


def task2() -> None:
    """Second test task."""
    print("task2")


@pytest.fixture
def scheduler_app_with_tasks(scheduler_app: SchedulerApp) -> SchedulerApp:
    """Scheduler app with two registered tasks."""
    scheduler_app.interval(hours=1)(task1)
    scheduler_app.interval(hours=2)(task2)
    return scheduler_app


@pytest.fixture
def client_with_tasks(scheduler_app_with_tasks: SchedulerApp) -> TestClient:
    """Test client with scheduler app that has tasks."""
    app = FastAPI(lifespan=scheduler_app_with_tasks.lifespan)
    scheduler_app_with_tasks.setup(app)
    return TestClient(app)


@pytest.mark.integration
def test_list_tasks(scheduler_app_with_tasks: SchedulerApp, client_with_tasks: TestClient) -> None:
    """Test list tasks endpoint."""
    # Arrange
    expected_tasks_count = 2
    api_prefix = scheduler_app_with_tasks.api.prefix

    # Act
    with client_with_tasks as client:
        response = client.get(f"{api_prefix}/tasks")
        tasks = TypeAdapter(list[Task]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(tasks) == expected_tasks_count

    task_ids = {task.id for task in tasks}
    assert "tests.integration.test_router_tasks:task1" in task_ids
    assert "tests.integration.test_router_tasks:task2" in task_ids


@pytest.mark.integration
def test_get_task(scheduler_app: SchedulerApp) -> None:
    """Test get task by ID endpoint."""
    # Arrange
    scheduler_app.interval(hours=1)(task1)
    task_id = "tests.integration.test_router_tasks:task1"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/tasks/{task_id}")
        task = Task.model_validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert task.id == task_id
    assert task.job_executor == "async"


@pytest.mark.integration
def test_get_task_not_found(scheduler_app: SchedulerApp) -> None:
    """Test get task returns 404 for non-existent task."""
    # Arrange
    scheduler_app.interval(hours=1)(task1)
    non_existent_task_id = "non-existent-task"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/tasks/{non_existent_task_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_list_tasks_pagination(scheduler_app_with_tasks: SchedulerApp, client_with_tasks: TestClient) -> None:
    """Test list tasks with pagination."""
    # Arrange
    expected_limit = 1
    expected_total_count = "2"
    api_prefix = scheduler_app_with_tasks.api.prefix

    # Act
    with client_with_tasks as client:
        response = client.get(f"{api_prefix}/tasks?limit={expected_limit}&offset=0")
        tasks = TypeAdapter(list[Task]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert response.headers["X-Total-Count"] == expected_total_count
    assert len(tasks) == expected_limit


@pytest.mark.integration
def test_list_tasks_pagination_offset(scheduler_app_with_tasks: SchedulerApp, client_with_tasks: TestClient) -> None:
    """Test list tasks with pagination offset."""
    # Arrange
    expected_limit = 1
    expected_offset = 1
    expected_total_count = "2"
    api_prefix = scheduler_app_with_tasks.api.prefix

    # Act
    with client_with_tasks as client:
        response = client.get(f"{api_prefix}/tasks?limit={expected_limit}&offset={expected_offset}")
        tasks = TypeAdapter(list[Task]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert response.headers["X-Total-Count"] == expected_total_count
    assert len(tasks) == expected_limit


@pytest.mark.integration
def test_list_tasks_empty(scheduler_app: SchedulerApp) -> None:
    """Test list tasks when no tasks are registered."""
    # Arrange
    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/tasks")
        tasks = TypeAdapter(list[Task]).validate_json(response.text)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(tasks) == 0
