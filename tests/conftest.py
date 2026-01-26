"""Tests Config."""

import pytest
from fastapi import FastAPI
from pydantic import SecretStr

from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.config import PostgresConfig, RedisConfig


@pytest.fixture
def anyio_backend() -> str:
    """AnyIO backend set to asyncio."""
    return "asyncio"


@pytest.fixture
def redis_config() -> RedisConfig:
    """Redis config fixture."""
    return RedisConfig(
        host="localhost",
        username="username",
        password=SecretStr("password"),
        db=1,
    )


@pytest.fixture
def postgres_config() -> PostgresConfig:
    """Postgres config fixture."""
    return PostgresConfig(
        host="localhost",
        db="test",
        username="username",
        password=SecretStr("password"),
    )


@pytest.fixture
def scheduler_app() -> SchedulerApp:
    """Create a scheduler app instance."""
    return SchedulerApp()


@pytest.fixture
def fastapi_app(scheduler_app: SchedulerApp) -> FastAPI:
    """Create a FastAPI app with scheduler lifespan."""
    app = FastAPI(lifespan=scheduler_app.lifespan)
    scheduler_app.setup(app)
    return app


def sample_task() -> None:
    """Sample task function for testing."""
