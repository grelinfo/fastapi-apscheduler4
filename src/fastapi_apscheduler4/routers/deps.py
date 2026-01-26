"""FastAPI Dependencies."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Query

from fastapi_apscheduler4.config import SchedulerAPIEnvConfig
from fastapi_apscheduler4.dtos import LimitOffset


@lru_cache
def get_scheduler_api_config() -> SchedulerAPIEnvConfig:
    """Get the scheduler API configuration.

    Uses lru_cache to ensure the config is only instantiated once,
    but lazily on first use rather than at module import time.
    """
    return SchedulerAPIEnvConfig()


def limit_offset(
    config: Annotated[SchedulerAPIEnvConfig, Depends(get_scheduler_api_config)],
    limit: int | None = Query(None, ge=1, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> LimitOffset:
    """Limit Offset query parameters.

    Applies config-based defaults at runtime rather than at module import time.
    """
    if config is None:
        config = get_scheduler_api_config()
    if limit is None:
        limit = config.limit_default
    elif limit > config.limit_max:
        limit = config.limit_max
    return LimitOffset(limit=limit, offset=offset)


LimitOffsetQueryParams = Annotated[LimitOffset, Depends(limit_offset)]
