"""Test Settings."""

from fastapi_apscheduler4.settings import create_config_from_env_vars


def test_create_config_from_env_vars() -> None:
    """Test create config from environment variables."""
    # Act
    config = create_config_from_env_vars()

    # Assert
    assert config.auto_start is True

    # TODO(grelinfo): Add more assertions  # noqa: TD003, FIX002
