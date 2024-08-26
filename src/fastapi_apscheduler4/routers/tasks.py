"""FastAPI Router for tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import apscheduler as aps
from fastapi import APIRouter, Response

from fastapi_apscheduler4.config import SchedulerAPIConfig
from fastapi_apscheduler4.errors import NotFoundAPIError, UnexpectedAPIError
from fastapi_apscheduler4.routers.deps import LimitOffsetQueryParams
from fastapi_apscheduler4.schemas import Task
from fastapi_apscheduler4.utils import paginate, safe_error

if TYPE_CHECKING:
    from enum import Enum


class TasksAPIRouter(APIRouter):
    """Tasks API Router."""

    def __init__(
        self,
        apscheduler: aps.AsyncScheduler,
        *,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        responses: dict[int | str, dict[str, Any]] | None = None,
        dependency_overrides_provider: Any = None,  # noqa: ANN401
        include_in_schema: bool = True,
    ) -> None:
        """Initialize the API router."""
        super().__init__(
            prefix=prefix,
            tags=tags,
            responses=responses,
            dependency_overrides_provider=dependency_overrides_provider,
            include_in_schema=include_in_schema,
        )
        self.apscheduler = apscheduler

        self.add_api_route(
            "/tasks", self.get_task, methods=["GET"], response_model=list[Task], response_model_exclude_none=True
        )
        self.add_api_route(
            "/tasks/{id}",
            self.get_task,
            methods=["GET"],
            response_model=Task,
            response_model_exclude_none=True,
        )

    @classmethod
    def from_config(cls, apscheduler: aps.AsyncScheduler, config: SchedulerAPIConfig) -> TasksAPIRouter:
        """Create an API router from the configuration."""
        return cls(
            apscheduler=apscheduler,
            prefix=config.prefix,
            tags=config.tags,
            include_in_schema=config.include_in_schema,
        )

    async def list_tasks(self, response: Response, limit_offset: LimitOffsetQueryParams) -> list[aps.Task]:
        """List tasks."""
        with safe_error(UnexpectedAPIError):
            tasks = await self.apscheduler.data_store.get_tasks()
            return paginate(tasks, limit_offset, response)

    async def get_task(self, id: str) -> aps.Task:
        """Get a task by ID."""
        with safe_error(UnexpectedAPIError, allow=NotFoundAPIError):
            try:
                return await self.apscheduler.data_store.get_task(id)
            except aps.TaskLookupError as error:
                raise NotFoundAPIError(Task, id) from error
