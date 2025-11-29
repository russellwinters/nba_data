"""Shared helper utilities for the nba_data project."""

from lib.helpers.csv_helpers import write_csv
from lib.helpers.date_helpers import format_date_nba
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
    api_error_handler,
    convert_exception,
)
from lib.helpers.validation import (
    validate_player_id,
    validate_team_id,
    validate_season,
    validate_date,
    validate_game_id,
)

__all__ = [
    # Team helpers
    "normalize_team_id",
    # CSV helpers
    "write_csv",
    # Date helpers
    "format_date_nba",
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
    "api_error_handler",
    "convert_exception",
    # Validation helpers
    "validate_player_id",
    "validate_team_id",
    "validate_season",
    "validate_date",
    "validate_game_id",
]
