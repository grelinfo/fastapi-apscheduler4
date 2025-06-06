"""Test FastAPI-APScheduler4 App."""

import pytest
from apscheduler import RunState
from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler.eventbrokers.redis import RedisEventBroker
from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient
from typer import echo

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.config import (
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
    SchedulerAPIConfig,
    SchedulerConfig,
)
from fastapi_apscheduler4.errors import AlreadySetupError, ConfigNotFoundError


async def route_test(request: Request) -> PlainTextResponse:  # noqa: ARG001
    """Test route."""
    return PlainTextResponse("Hello, world!")


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


def test_app_lifespan(capsys: pytest.CaptureFixture[str]) -> None:
    """Test scheduler lifespan."""
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


def test_init_memory() -> None:
    """Test setup with memory config."""
    # Arrange
    config = SchedulerConfig(
        event_broker=EventBrokerType.MEMORY,
        data_store=DataStoreType.MEMORY,
    )

    # Act
    scheduler_app = SchedulerApp(scheduler=config)

    # Assert
    assert scheduler_app.event_broker is EventBrokerType.MEMORY
    assert scheduler_app.data_store is DataStoreType.MEMORY
    assert isinstance(scheduler_app.apscheduler.event_broker, LocalEventBroker)
    assert isinstance(scheduler_app.apscheduler.data_store, MemoryDataStore)


def test_init_redis(redis_config: RedisConfig) -> None:
    """Test init with redis."""
    # Arrange
    scheduler = SchedulerConfig(
        event_broker=EventBrokerType.REDIS,
    )
    # Act
    scheduler_app = SchedulerApp(scheduler=scheduler, redis=redis_config)

    # Assert
    assert scheduler_app.event_broker is EventBrokerType.REDIS
    assert isinstance(scheduler_app.apscheduler.event_broker, RedisEventBroker)
    assert isinstance(scheduler_app.apscheduler.data_store, MemoryDataStore)


def test_init_postgres(postgres_config: PostgresConfig) -> None:
    """Test init with postgres config."""
    # Arrange
    scheduler = SchedulerConfig(
        event_broker=EventBrokerType.POSTGRES,
        data_store=DataStoreType.POSTGRES,
    )

    # Act
    app_scheduler = SchedulerApp(scheduler=scheduler, postgres=postgres_config)

    # Assert
    assert app_scheduler.event_broker is EventBrokerType.POSTGRES
    assert app_scheduler.data_store is DataStoreType.POSTGRES
    assert isinstance(app_scheduler.apscheduler.event_broker, AsyncpgEventBroker)
    assert isinstance(app_scheduler.apscheduler.data_store, SQLAlchemyDataStore)


def test_init_config_not_found_error() -> None:
    """Test init with config not found error."""
    # Arrange
    scheduler = SchedulerConfig(
        event_broker=EventBrokerType.REDIS,
        data_store=DataStoreType.POSTGRES,
    )

    # Act
    with pytest.raises(ConfigNotFoundError):
        SchedulerApp(scheduler=scheduler)


@pytest.mark.parametrize("scheduler_api", [True, False])
def test_setup_api(scheduler_api: bool) -> None:
    """Test setup of api."""
    # Arrange
    app_scheduler = SchedulerApp(api=SchedulerAPIConfig(enabled=scheduler_api))
    app = FastAPI(lifespan=app_scheduler.lifespan)
    app_scheduler.setup(app)

    expected_status_code = status.HTTP_200_OK if scheduler_api else status.HTTP_404_NOT_FOUND

    # Act
    with TestClient(app) as client:
        response = client.get(SchedulerAPIConfig().prefix + "/schedules")

    # Assert
    assert response.status_code == expected_status_code


def test_already_setup_error() -> None:
    """Test already setup error."""
    # Arrange
    app_scheduler = SchedulerApp()
    app = FastAPI(lifespan=app_scheduler.lifespan)

    # Act
    app_scheduler.setup(app)
    with pytest.raises(AlreadySetupError):
        app_scheduler.setup(app)
