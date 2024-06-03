"""Tests Config."""

import pytest


@pytest.fixture()
def anyio_backend() -> str:
    """AnyIO backend set to asyncio."""
    return "asyncio"
