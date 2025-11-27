"""Shared error handling utilities for the nba_data project.

This module provides a consistent error handling strategy and standardized
logging format for all fetching modules. It establishes patterns that can
be used across the codebase to ensure uniform error reporting and handling.

Error Handling Strategy
-----------------------
The nba_data project follows these conventions for error handling:

1. **Return Types**: Functions that fetch data return:
   - A `pandas.DataFrame` on success (may be empty if no data found)
   - An empty `DataFrame` on recoverable errors (network issues, no data)
   - Raise exceptions for programming errors or critical failures

2. **When to Raise Exceptions**:
   - Invalid input parameters (ValidationError)
   - Entity not found when explicitly required (PlayerNotFoundError, etc.)
   - Critical API failures that should not be silently ignored

3. **When to Return Empty DataFrame**:
   - No data available for the given query
   - Transient API errors (with logging)
   - Optional entity lookups (e.g., team ID resolution)

4. **Logging Convention**:
   - Use the `log_error`, `log_warning`, `log_info` functions for consistent formatting
   - Include context (function name, parameters) in error messages
   - Log at appropriate levels: ERROR for failures, WARNING for recoverable issues

Usage:
    from lib.helpers.error_handling import log_error, log_warning, handle_api_errors

    @handle_api_errors
    def my_fetch_function(param):
        # function body
        pass
"""

import functools
import logging
import sys
from typing import Callable, Optional, TypeVar

import pandas as pd

from lib.helpers.exceptions import (
    APIError,
    APITimeoutError,
    NBADataError,
)

# Configure module logger
logger = logging.getLogger("nba_data")

# Type variable for generic function return type
T = TypeVar("T")


def setup_logging(level: int = logging.INFO, format_string: str = None) -> None:
    """Configure logging for the nba_data project.

    Args:
        level: Logging level (default: INFO)
        format_string: Optional custom format string
    """
    if format_string is None:
        format_string = "[%(levelname)s] %(name)s - %(message)s"

    # Avoid adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(handler)

    logger.setLevel(level)


def log_error(message: str, context: Optional[dict] = None) -> None:
    """Log an error message with optional context.

    Uses print statements for console output to maintain consistency with
    the existing codebase style. Also logs to the nba_data logger for
    applications that have configured logging.

    Args:
        message: Error message to log
        context: Optional dictionary of contextual information

    Example:
        log_error("Failed to fetch player", {"player_id": 12345, "season": "2023-24"})
    """
    formatted_message = _format_log_message(message, context)
    print(f"Error: {formatted_message}")


def log_warning(message: str, context: Optional[dict] = None) -> None:
    """Log a warning message with optional context.

    Uses print statements for console output to maintain consistency with
    the existing codebase style. Also logs to the nba_data logger for
    applications that have configured logging.

    Args:
        message: Warning message to log
        context: Optional dictionary of contextual information

    Example:
        log_warning("No data found", {"team_id": "LAL", "date_from": "2024-01-01"})
    """
    formatted_message = _format_log_message(message, context)
    print(f"Warning: {formatted_message}")


def log_info(message: str, context: Optional[dict] = None) -> None:
    """Log an info message with optional context.

    Uses print statements for console output to maintain consistency with
    the existing codebase style. Also logs to the nba_data logger for
    applications that have configured logging.

    Args:
        message: Info message to log
        context: Optional dictionary of contextual information

    Example:
        log_info("Fetching player data", {"player_id": 12345})
    """
    formatted_message = _format_log_message(message, context)
    print(formatted_message)


def _format_log_message(message: str, context: Optional[dict] = None) -> str:
    """Format a log message with optional context.

    Args:
        message: Base message
        context: Optional dictionary of contextual information

    Returns:
        Formatted message string
    """
    if context:
        context_str = ", ".join(f"{k}={v!r}" for k, v in context.items())
        return f"{message} [{context_str}]"
    return message


def handle_api_errors(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
    """Decorator to handle common API errors with consistent behavior.

    This decorator wraps API-calling functions and provides:
    - Consistent error logging
    - Conversion of exceptions to empty DataFrames for recoverable errors
    - Re-raising of critical errors

    Args:
        func: Function that makes API calls and returns a DataFrame

    Returns:
        Wrapped function with error handling

    Example:
        @handle_api_errors
        def fetch_player_data(player_id):
            # API call that might fail
            return df
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> pd.DataFrame:
        try:
            return func(*args, **kwargs)
        except APITimeoutError as e:
            log_error(
                f"API timeout in {func.__name__}",
                {"timeout": e.timeout_seconds, "endpoint": e.endpoint},
            )
            return pd.DataFrame()
        except APIError as e:
            log_error(
                f"API error in {func.__name__}",
                {"status": e.status_code, "endpoint": e.endpoint},
            )
            return pd.DataFrame()
        except NBADataError as e:
            # Re-raise NBADataError subclasses that aren't API errors
            # (e.g., ValidationError, PlayerNotFoundError)
            raise
        except Exception as e:
            log_error(f"Unexpected error in {func.__name__}: {e}")
            return pd.DataFrame()

    return wrapper


def safe_api_call(
    func: Callable[..., T],
    *args,
    default: T = None,
    context: Optional[dict] = None,
    **kwargs,
) -> T:
    """Execute an API call with error handling and logging.

    This function provides a consistent way to make API calls with
    proper error handling and logging.

    Args:
        func: Function to call
        *args: Positional arguments to pass to func
        default: Default value to return on error
        context: Optional context dictionary for logging
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default value on error

    Example:
        result = safe_api_call(
            api_endpoint.get_data,
            player_id=12345,
            default=[],
            context={"operation": "fetch_player"}
        )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        func_name = getattr(func, "__name__", str(func))
        log_context = {"function": func_name}
        if context:
            log_context.update(context)
        log_error(f"API call failed: {e}", log_context)
        return default
