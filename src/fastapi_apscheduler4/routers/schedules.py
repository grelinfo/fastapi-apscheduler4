"""FastAPI Router for schedules."""

from __future__ import annotations

from typing import TYPE_CHECKING

import apscheduler as aps
from fastapi import APIRouter, Query, Response, status

from fastapi_apscheduler4 import logger
from fastapi_apscheduler4.config import APIConfig
from fastapi_apscheduler4.errors import DeleteNotAllowedAPIError, NotFoundAPIError, UnexpectedAPIError
from fastapi_apscheduler4.routers.deps import LimitOffsetQueryParams
from fastapi_apscheduler4.schemas import SCHEDULE_PREFIX, Schedule
from fastapi_apscheduler4.utils import paginate, safe_error

if TYPE_CHECKING:
    from enum import Enum


class SchedulesAPIRouter(APIRouter):
    """Schedules API Router."""

    def __init__(
        self,
        apscheduler: aps.AsyncScheduler,
        *,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        include_in_schema: bool = True,
    ) -> None:
        """Initialize the API router."""
        super().__init__(
            prefix=prefix,
            tags=tags,
            include_in_schema=include_in_schema,
        )
        self.apscheduler = apscheduler
        self.add_api_route(
            "/schedules",
            self.list_schedules,
            methods=["GET"],
            response_model=list[Schedule],
            response_model_exclude_none=True,
        )
        self.add_api_route(
            "/schedules/{id}",
            self.get_schedule,
            methods=["GET"],
            response_model=Schedule,
            response_model_exclude_none=True,
        )
        self.add_api_route(
            "/schedules/{id}",
            self.delete_schedule,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
            response_model=None,
        )

    @classmethod
    def from_config(cls, apscheduler: aps.AsyncScheduler, config: APIConfig) -> SchedulesAPIRouter:
        """Create an API router from the configuration."""
        return cls(
            apscheduler=apscheduler,
            prefix=config.prefix,
            tags=config.tags,
            include_in_schema=config.include_in_schema,
        )

    async def list_schedules(self, response: Response, limit_offset: LimitOffsetQueryParams) -> list[aps.Schedule]:
        """List schedules."""
        with safe_error(UnexpectedAPIError):
            schedules = await self.apscheduler.get_schedules()
            return paginate(schedules, limit_offset, response)

    async def get_schedule(self, id: str) -> aps.Schedule:
        """Get a schedule by ID."""
        with safe_error(UnexpectedAPIError, allow=NotFoundAPIError):
            try:
                return await self.apscheduler.get_schedule(id)
            except aps.ScheduleLookupError as error:
                raise NotFoundAPIError(Schedule, id) from error

    async def delete_schedule(
        self,
        id: str,
        force: bool = Query(  # noqa: FBT001
            False,  # noqa: FBT003
            description=f"True will force deleting auto schedules (prefixed with '{SCHEDULE_PREFIX}').",
        ),
    ) -> None:
        """Delete a schedule by ID."""
        with safe_error(UnexpectedAPIError, allow=(DeleteNotAllowedAPIError, NotFoundAPIError)):
            await self.get_schedule(id)

            if id.startswith(SCHEDULE_PREFIX):
                if not force:
                    raise DeleteNotAllowedAPIError(Schedule, id)
                logger.warning(f"Schedule ID {id} deleted with force.")

            await self.apscheduler.remove_schedule(id)
