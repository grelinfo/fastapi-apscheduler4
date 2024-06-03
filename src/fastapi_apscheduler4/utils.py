"""Utilities."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import tzinfo
from enum import Enum
from typing import TYPE_CHECKING, ParamSpec, TypeVar, overload

from fastapi import Response, status

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from fastapi_apscheduler4.dtos import LimitOffset
    from fastapi_apscheduler4.errors import UnexpectedErrorProtocol

T = TypeVar("T")


RT = TypeVar("RT")
P = ParamSpec("P")


@contextmanager
def safe_error(
    default: type[UnexpectedErrorProtocol], *, allow: Iterable[type[Exception]] | type[Exception] | None = None
) -> Generator[None, None, None]:
    """Decorator or contextmanager to catch all unexpected errors and raise a default error.

    Args:
        default: Error to raise if a non expected error occurs.
        allow: Allowed error(s) to pass through.
    """
    allow = [allow] if isinstance(allow, type) else allow or []

    try:
        yield
    except BaseException as error:
        if not any(isinstance(error, allowed) for allowed in allow):
            raise default(error) from error
        raise


@overload
def enforce_enum_name(value: Enum) -> str: ...
@overload
def enforce_enum_name(value: T) -> str | T: ...
def enforce_enum_name(value: Enum | T) -> str | T:
    """Enforce Enum name if Enum else return value."""
    if isinstance(value, Enum):
        return value.name
    return value


@overload
def transform_tzinfo_to_str(value: tzinfo) -> str: ...
@overload
def transform_tzinfo_to_str(value: T) -> str | T: ...
def transform_tzinfo_to_str(value: tzinfo | T) -> str | T:
    """Transform tzinfo to string."""
    if isinstance(value, tzinfo):
        return value.tzname(None) or "UTC"
    return value


def paginate(items: list[T], limit_offset: LimitOffset, response: Response) -> list[T]:
    """Paginate items."""
    total_count = len(items)
    paginated = items[limit_offset.offset : limit_offset.offset + limit_offset.limit]

    response.headers["X-Total-Count"] = str(total_count)
    if total_count != len(paginated):
        response.status_code = status.HTTP_206_PARTIAL_CONTENT

    return paginated


def dict_add_if_not_none(data: dict[str, T], key: str, value: T | None) -> None:
    """Add key-value pair to dictionary if value is not None."""
    if value is not None:
        data[key] = value
