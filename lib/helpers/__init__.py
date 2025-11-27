"""Helper utilities for the nba_data project."""

from lib.helpers.exceptions import (
    NBADataError,
    EntityNotFoundError,
    PlayerNotFoundError,
    TeamNotFoundError,
    GameNotFoundError,
    APIError,
    APITimeoutError,
    APIRateLimitError,
    ValidationError,
)
from lib.helpers.error_handling import (
    log_error,
    log_warning,
    log_info,
    handle_api_errors,
    safe_api_call,
    setup_logging,
)

__all__ = [
    # Exceptions
    "NBADataError",
    "EntityNotFoundError",
    "PlayerNotFoundError",
    "TeamNotFoundError",
    "GameNotFoundError",
    "APIError",
    "APITimeoutError",
    "APIRateLimitError",
    "ValidationError",
    # Error handling utilities
    "log_error",
    "log_warning",
    "log_info",
    "handle_api_errors",
    "safe_api_call",
    "setup_logging",
]
