"""Test Utilities."""

import pytest
from fastapi import Response, status
from fastapi_apscheduler4.dtos import LimitOffset
from fastapi_apscheduler4.errors import DeleteNotAllowedAPIError, NotFoundAPIError, UnexpectedAPIError
from fastapi_apscheduler4.utils import paginate, safe_error
from pydantic import BaseModel


def test_safe_error_decorator() -> None:
    """Test safe error decorator."""

    # Arrange
    @safe_error(UnexpectedAPIError, allow=NotFoundAPIError)
    def success1() -> None:
        """Test function that succeeds."""

    @safe_error(UnexpectedAPIError, allow=(NotFoundAPIError, DeleteNotAllowedAPIError))
    def success2() -> None:
        """Test function that succeeds."""

    @safe_error(UnexpectedAPIError, allow=NotFoundAPIError)
    def always_raise_value_error1() -> None:
        """Test function that only raises ValueError."""
        raise ValueError("error")

    @safe_error(UnexpectedAPIError, allow=(NotFoundAPIError, DeleteNotAllowedAPIError))
    def always_raise_value_error2() -> None:
        """Test function that only raises ValueError."""
        raise ValueError("error")

    @safe_error(UnexpectedAPIError, allow=NotFoundAPIError)
    def always_raise_not_found_api_error() -> None:
        """Test function that only raises NotFoundAPIError."""
        raise NotFoundAPIError(BaseModel, "test")

    @safe_error(UnexpectedAPIError, allow=(NotFoundAPIError, DeleteNotAllowedAPIError))
    def always_raise_delete_not_allowed_api_error() -> None:
        """Test function that only raises DeleteNotAllowedAPIError."""
        raise DeleteNotAllowedAPIError(BaseModel, "test")

    # Act
    success1()
    success2()
    with pytest.raises(UnexpectedAPIError):
        always_raise_value_error1()
    with pytest.raises(UnexpectedAPIError):
        always_raise_value_error2()
    with pytest.raises(NotFoundAPIError):
        always_raise_not_found_api_error()
    with pytest.raises(DeleteNotAllowedAPIError):
        always_raise_delete_not_allowed_api_error()


def test_safe_error_contextmanager() -> None:
    """Test safe error context manager."""

    # Arrange
    def success1() -> None:
        """Test function that succeeds."""
        with safe_error(UnexpectedAPIError, allow=NotFoundAPIError):
            pass

    def success2() -> None:
        """Test function that succeeds."""
        with safe_error(UnexpectedAPIError, allow=(NotFoundAPIError, DeleteNotAllowedAPIError)):
            pass

    def always_raise_value_error1() -> None:
        """Test function that only raises ValueError."""
        with safe_error(UnexpectedAPIError, allow=NotFoundAPIError):
            raise ValueError("error")

    def always_raise_value_error2() -> None:
        """Test function that only raises ValueError."""
        with safe_error(UnexpectedAPIError, allow=(NotFoundAPIError, DeleteNotAllowedAPIError)):
            raise ValueError("error")

    def always_raise_not_found_api_error() -> None:
        """Test function that only raises NotFoundAPIError."""
        with safe_error(UnexpectedAPIError, allow=NotFoundAPIError):
            raise NotFoundAPIError(BaseModel, "test")

    def always_raise_delete_not_allowed_api_error() -> None:
        """Test function that only raises DeleteNotAllowedAPIError."""
        with safe_error(UnexpectedAPIError, allow=(NotFoundAPIError, DeleteNotAllowedAPIError)):
            raise DeleteNotAllowedAPIError(BaseModel, "test")

    # Act
    success1()
    success2()
    with pytest.raises(UnexpectedAPIError):
        always_raise_value_error1()
    with pytest.raises(UnexpectedAPIError):
        always_raise_value_error2()
    with pytest.raises(NotFoundAPIError):
        always_raise_not_found_api_error()
    with pytest.raises(DeleteNotAllowedAPIError):
        always_raise_delete_not_allowed_api_error()


def test_paginate() -> None:
    """Test paginate."""
    # Arrange
    items = [1, 2, 3, 4, 5]
    limit_offset_partial = LimitOffset(limit=2, offset=0)
    response_partial = Response()
    limit_offset_full = LimitOffset(limit=5, offset=0)
    response_full = Response()

    # Act
    partial_items = paginate(items, limit_offset_partial, response_partial)
    full_items = paginate(items, limit_offset_full, response_full)

    # Assert
    assert partial_items == [1, 2]
    assert response_partial.status_code == status.HTTP_206_PARTIAL_CONTENT
    assert response_partial.headers["X-Total-Count"] == "5"
    assert full_items == [1, 2, 3, 4, 5]
    assert response_full.status_code == status.HTTP_200_OK
    assert response_full.headers["X-Total-Count"] == "5"
