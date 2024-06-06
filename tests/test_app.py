"""Test FastAPI-APScheduler4 App."""

import pytest
from apscheduler import RunState
from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler.eventbrokers.redis import RedisEventBroker
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient
from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.config import (
    APIConfig,
    APSchedulerConfig,
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisChannelConfig,
    RedisConfig,
    SchedulerConfig,
)
from fastapi_apscheduler4.errors import AlreadySetupError, InvalidConfigError
from fastapi_apscheduler4.scheduler import Scheduler
from pydantic import SecretStr
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from typer import echo


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


@pytest.fixture()
def config() -> SchedulerConfig:
    """Get scheduler config."""
    return SchedulerConfig()  # pyright: ignore[reportCallIssue]


def test_include_scheduler(config: SchedulerConfig) -> None:
    """Test scheduler include another scheduler."""
    # Arrange
    schedules_count = 2
    scheduler_app = SchedulerApp(config=config)

    scheduler1 = Scheduler()
    scheduler2 = Scheduler()

    @scheduler1.interval(seconds=1)
    def every_second() -> None:
        """Test register every second."""

    @scheduler2.interval(minutes=1)
    async def every_minute() -> None:
        """Test register async every minute."""

    # Act
    scheduler_app.include(scheduler1)
    scheduler_app.include(scheduler2)

    # Assert
    assert len(scheduler_app._scheduler._schedules) == schedules_count
    scheduler1_func, scheduler1_trigger = scheduler_app._scheduler._schedules[0]
    scheduler2_func, scheduler2_trigger = scheduler_app._scheduler._schedules[1]

    assert scheduler1_func == every_second
    assert isinstance(scheduler1_trigger, IntervalTrigger)
    assert scheduler1_trigger.seconds == 1
    assert scheduler1_trigger.minutes == 0

    assert scheduler2_func == every_minute
    assert isinstance(scheduler2_trigger, IntervalTrigger)
    assert scheduler2_trigger.seconds == 0
    assert scheduler2_trigger.minutes == 1


def test_scheduler_lifespan(config: SchedulerConfig, capsys: pytest.CaptureFixture[str]) -> None:
    """Test scheduler lifespan."""
    # Arrange
    scheduler_app = SchedulerApp(config)
    scheduler_app._scheduler.interval(seconds=1)(echo_test1)

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


def test_setup_memory() -> None:
    """Test setup with memory config."""
    # Arrange
    config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            event_broker=EventBrokerType.MEMORY,
            data_store=DataStoreType.MEMORY,
        )
    )

    # Act
    scheduler_app = SchedulerApp(config=config)

    # Assert
    assert isinstance(config.apscheduler, APSchedulerConfig)
    assert scheduler_app.event_broker is EventBrokerType.MEMORY
    assert scheduler_app.data_store is DataStoreType.MEMORY
    assert isinstance(scheduler_app.apscheduler.event_broker, LocalEventBroker)
    assert isinstance(scheduler_app.apscheduler.data_store, MemoryDataStore)


def test_setup_redis() -> None:
    """Test setup with redis config."""
    # Arrange
    config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            event_broker=EventBrokerType.REDIS,
            redis=RedisConfig(
                host="localhost",
                port=6379,
                db=0,
                user="username",
                password=SecretStr("password"),
            ),
        )
    )
    config_without_redis = SchedulerConfig(apscheduler=APSchedulerConfig(event_broker=EventBrokerType.REDIS))
    config_with_channel = SchedulerConfig(
        apscheduler=APSchedulerConfig(event_broker=EventBrokerType.REDIS, redis=RedisChannelConfig(channel="test"))
    )
    redis = Redis.from_url("redis://username:password@localhost:6379/0")

    # Act
    scheduler_app = SchedulerApp(config=config)
    scheduler_app_custom_redis = SchedulerApp(config=config, redis=redis)
    scheduler_app_without_config = SchedulerApp(config_with_channel, redis=redis)
    with pytest.raises(InvalidConfigError, match="redis"):
        SchedulerApp(config=config_without_redis)
    with pytest.raises(InvalidConfigError, match="redis"):
        SchedulerApp(config=config_with_channel)
    with pytest.raises(InvalidConfigError, match="redis"):
        SchedulerApp(redis=redis)

    # Assert
    assert isinstance(config.apscheduler, APSchedulerConfig)
    assert scheduler_app.event_broker is EventBrokerType.REDIS
    assert isinstance(scheduler_app.apscheduler.event_broker, RedisEventBroker)
    assert isinstance(scheduler_app.apscheduler.data_store, MemoryDataStore)

    assert isinstance(config_without_redis.apscheduler, APSchedulerConfig)
    assert scheduler_app_custom_redis.event_broker is EventBrokerType.REDIS
    assert isinstance(scheduler_app_custom_redis.apscheduler.event_broker, RedisEventBroker)
    assert isinstance(scheduler_app_custom_redis.apscheduler.data_store, MemoryDataStore)

    assert scheduler_app_without_config.event_broker is EventBrokerType.REDIS
    assert isinstance(scheduler_app_without_config.apscheduler.event_broker, RedisEventBroker)
    assert isinstance(scheduler_app_without_config.apscheduler.data_store, MemoryDataStore)


def test_setup_postgres(
    config: SchedulerConfig,
) -> None:
    """Test setup with postgres config."""
    # Arrange
    config = SchedulerConfig(
        apscheduler=APSchedulerConfig(
            event_broker=EventBrokerType.POSTGRES,
            data_store=DataStoreType.POSTGRES,
            postgres=PostgresConfig(
                host="localhost",
                port=5432,
                db="test",
                user="username",
                password=SecretStr("password"),
            ),
        )
    )
    config_without_postgres = SchedulerConfig(apscheduler=APSchedulerConfig(event_broker=EventBrokerType.POSTGRES))
    engine = create_async_engine("postgresql+asyncpg://username:password@localhost:5432/test")

    # Act
    app_scheduler = SchedulerApp(config=config)
    app_schedule_engine = SchedulerApp(config=config, engine=engine)
    app_scheduler_without_config = SchedulerApp(engine=engine)
    with pytest.raises(InvalidConfigError, match="postgres"):
        SchedulerApp(config=config_without_postgres)

    # Assert
    assert isinstance(config.apscheduler, APSchedulerConfig)
    assert app_scheduler.event_broker is EventBrokerType.POSTGRES
    assert app_scheduler.data_store is DataStoreType.POSTGRES
    assert isinstance(app_scheduler.apscheduler.event_broker, AsyncpgEventBroker)
    assert isinstance(app_scheduler.apscheduler.data_store, SQLAlchemyDataStore)

    assert isinstance(config_without_postgres.apscheduler, APSchedulerConfig)
    assert app_schedule_engine.event_broker is EventBrokerType.POSTGRES
    assert app_schedule_engine.data_store is DataStoreType.POSTGRES
    assert isinstance(app_schedule_engine.apscheduler.event_broker, AsyncpgEventBroker)
    assert isinstance(app_schedule_engine.apscheduler.data_store, SQLAlchemyDataStore)

    assert app_scheduler_without_config.event_broker is EventBrokerType.POSTGRES
    assert isinstance(app_scheduler_without_config.apscheduler.event_broker, AsyncpgEventBroker)


@pytest.mark.parametrize("scheduler_api", [True, False])
def test_setup_api(scheduler_api: bool) -> None:
    """Test setup of api."""
    # Arrange
    config = SchedulerConfig(api=APIConfig(enabled=scheduler_api))
    app_scheduler = SchedulerApp(config=config)
    app = FastAPI(lifespan=app_scheduler.lifespan)
    app_scheduler.setup(app)

    expected_status_code = status.HTTP_200_OK if scheduler_api else status.HTTP_404_NOT_FOUND

    # Act
    with TestClient(app) as client:
        response = client.get(APIConfig().prefix + "/schedules")

    # Assert
    assert response.status_code == expected_status_code


def test_already_setup_error(config: SchedulerConfig) -> None:
    """Test already setup error."""
    # Arrange
    app_scheduler = SchedulerApp(config=config)
    app = FastAPI(lifespan=app_scheduler.lifespan)

    # Act
    app_scheduler.setup(app)
    with pytest.raises(AlreadySetupError):
        app_scheduler.setup(app)
