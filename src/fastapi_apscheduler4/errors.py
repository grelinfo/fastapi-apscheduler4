"""Errors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException, status

from fastapi_apscheduler4 import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import BaseModel


class FastAPIAPScheduler4Error(Exception):
    """FastAPI APScheduler Error.

    Base class for all errors.
    """


class UnexpectedErrorProtocol(BaseException, ABC):
    """Unexpected Error Protocol.

    Protocol for unexpected errors needed by `safe_error` decorator.
    """

    @abstractmethod
    def __init__(self, exception: BaseException) -> None:
        """Initialize the error."""


class SetupError(FastAPIAPScheduler4Error):
    """Setup Error.

    Base class for all setup errors.
    """


class AlreadySetupError(SetupError):
    """Already Setup Error.

    Raised when the setup is already done and cannot be done again.
    """

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("FastAPIAPScheduler4 is already setup.")


class ConfigError(FastAPIAPScheduler4Error):
    """Configuration Error.

    Raised when the configuration is invalid.
    """


class InvalidConfigError(ConfigError):
    """Invalid Configuration Error.

    Raised when the configuration is missing.
    """

    def __init__(self, loc: str, detail: str) -> None:
        """Initialize the error."""
        super().__init__(f"Invalid configuration at {loc}: {detail}")


class ScheduleAlreadyExistsError(FastAPIAPScheduler4Error, ValueError):
    """Schedule Already Exists Error.

    Raised when trying to add a schedule that already exists.
    """

    def __init__(self, func: Callable[..., Any]) -> None:
        """Initialize the error."""
        super().__init__(f"Schedule for function {func.__name__} already exists.")


class APIError(FastAPIAPScheduler4Error, HTTPException):
    """API Error.

    Base class for all resource errors.
    """


class UnexpectedAPIError(APIError, UnexpectedErrorProtocol):
    """Unexpected API Error.

    Default error for all unexpected errors from the API.
    """

    def __init__(self, exception: BaseException) -> None:
        """Initialize the error."""
        detail = f"Unexpected error: {exception} ({type(exception).__name__})"
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        logger.exception(exception)


class NotFoundAPIError(APIError):
    """Not Found API Error.

    Raised when a resource is not found from the API.
    """

    def __init__(self, model: type[BaseModel], id: str) -> None:
        """Initialize the error."""
        detail = f"{model.__name__} with ID {id} not found."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class DeleteNotAllowedAPIError(APIError):
    """Delete Not Allowed API Error.

    Raised when a resource does not allow delete operation from the API.
    """

    def __init__(self, model: type, id: str) -> None:
        """Initialize the error."""
        detail = f"{model.__name__} with ID {id} does not allow delete."
        super().__init__(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=detail)
