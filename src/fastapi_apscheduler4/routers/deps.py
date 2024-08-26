"""FastAPI Dependencies."""

from typing import Annotated

from fastapi import Depends, Query

from fastapi_apscheduler4.config import SchedulerAPIEnvConfig
from fastapi_apscheduler4.dtos import LimitOffset

_config = SchedulerAPIEnvConfig()  # pyright: ignore[reportCallIssue]


def limit_offset(
    limit: int = Query(_config.limit_default, ge=1, le=_config.limit_max, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> LimitOffset:
    """Limit Offset query parameters."""
    return LimitOffset(limit=limit, offset=offset)


LimitOffsetQueryParams = Annotated[LimitOffset, Depends(limit_offset)]
