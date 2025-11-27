"""Shared helper utilities for the nba_data project."""

from lib.helpers.team_helpers import normalize_team_id
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
    # Team helpers
    "normalize_team_id",
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
