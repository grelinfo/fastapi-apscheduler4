"""Test Tasks API Router."""

# ruff: noqa: T201

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.schemas import Task


def echo_task1() -> None:
    """Test function 1."""
    print("task1")


def echo_task2() -> None:
    """Test function 2."""
    print("task2")


def test_list_tasks() -> None:
    """Test list tasks endpoint."""
    # Arrange
    scheduler_app = SchedulerApp()
    scheduler_app.interval(hours=1)(echo_task1)
    scheduler_app.interval(hours=2)(echo_task2)
    expected_tasks_count = 2

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(scheduler_app.api.prefix + "/tasks")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    tasks = TypeAdapter(list[Task]).validate_json(response.text)
    assert len(tasks) == expected_tasks_count

    task_ids = {task.id for task in tasks}
    assert "tests.test_router_tasks:echo_task1" in task_ids
    assert "tests.test_router_tasks:echo_task2" in task_ids


def test_get_task() -> None:
    """Test get task by ID endpoint."""
    # Arrange
    scheduler_app = SchedulerApp()
    scheduler_app.interval(hours=1)(echo_task1)
    task_id = "tests.test_router_tasks:echo_task1"

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/tasks/{task_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    task = Task.model_validate_json(response.text)
    assert task.id == task_id
    assert task.job_executor == "async"


def test_get_task_not_found() -> None:
    """Test get task returns 404 for non-existent task."""
    # Arrange
    scheduler_app = SchedulerApp()
    scheduler_app.interval(hours=1)(echo_task1)

    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)

    # Act
    with TestClient(app) as client:
        response = client.get(f"{scheduler_app.api.prefix}/tasks/non-existent-task")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
