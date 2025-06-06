"""Tests Config."""

import pytest
from pydantic import SecretStr

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
