"""Test on Postgres with testcontainers."""
# ruff: noqa: T201

from collections.abc import Generator

import pytest
from apscheduler import RunState
from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from fastapi_apscheduler4 import SchedulerApp


async def route_test(request: Request) -> PlainTextResponse:  # noqa: ARG001
    """Test route."""
    return PlainTextResponse("Hello, world!")


def echo_test1() -> None:
    """Test function 1."""
    print("test")


@pytest.fixture
def postgres_container(monkeypatch: pytest.MonkeyPatch) -> Generator[PostgresContainer, None, None]:
    """Create a Postgres container."""
    # PostgresContainer has built-in defaults: user=test, password=test, dbname=test
    container = PostgresContainer("postgres:latest")

    with container as postgres:
        # Set environment variables for the app to connect
        monkeypatch.setenv("POSTGRES_HOST", postgres.get_container_host_ip())
        monkeypatch.setenv("POSTGRES_PORT", str(postgres.get_exposed_port(5432)))
        monkeypatch.setenv("POSTGRES_DB", "test")
        monkeypatch.setenv("POSTGRES_USER", "test")
        monkeypatch.setenv("POSTGRES_PASSWORD", "test")

        yield postgres


@pytest.mark.usefixtures("postgres_container")
def test_app_postgres(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test scheduler app."""
    # Arrange

    scheduler_app = SchedulerApp()
    scheduler_app.interval(seconds=1)(echo_test1)

    app = FastAPI(lifespan=scheduler_app.lifespan)
    app.add_route("/", route_test, methods=["GET"])

    scheduler_app.setup(app)

    # Act
    state_before = scheduler_app.apscheduler.state
    with TestClient(app) as client:
        state_running = scheduler_app.apscheduler.state
        response = client.get("/")
    state_after = scheduler_app.apscheduler.state

    # Assert
    assert state_before == RunState.stopped
    assert state_running == RunState.started
    assert state_after == RunState.stopped
    assert "test" in capsys.readouterr().out
    assert response.status_code == status.HTTP_200_OK
