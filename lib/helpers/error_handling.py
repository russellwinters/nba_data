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

    # Or use the context manager for more control:
    from lib.helpers.error_handling import api_error_handler

    with api_error_handler(context={"player_id": 12345}):
        result = api_endpoint.get_data()
"""

import functools
import logging
import socket
import sys
from contextlib import contextmanager
from typing import Callable, Generator, Optional, TypeVar

import pandas as pd
import requests

from lib.helpers.exceptions import (
    APIError,
    APIRateLimitError,
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


def convert_exception(exc: Exception, endpoint: str = None) -> Exception:
    """Convert common network/HTTP exceptions to custom exception types.

    This function examines the exception type and converts it to the
    appropriate custom exception class for consistent error handling.

    Args:
        exc: The original exception
        endpoint: Optional endpoint name for context

    Returns:
        A custom exception (APITimeoutError, APIRateLimitError, APIError)
        or the original exception if it cannot be converted.

    Example:
        try:
            response = requests.get(url)
        except Exception as e:
            raise convert_exception(e, endpoint="player_stats")
    """
    # Handle timeout exceptions
    if isinstance(exc, (requests.exceptions.Timeout, socket.timeout)):
        return APITimeoutError(endpoint=endpoint)

    # Handle connection-related exceptions
    if isinstance(exc, requests.exceptions.ConnectionError):
        return APIError(
            message=f"Connection error: {exc}",
            endpoint=endpoint,
        )

    # Handle HTTP errors with status codes
    if isinstance(exc, requests.exceptions.HTTPError):
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None) if response else None

        # Check for rate limiting
        if status_code == 429:
            retry_after = None
            if response is not None:
                retry_after_header = response.headers.get("Retry-After")
                if retry_after_header:
                    try:
                        retry_after = int(retry_after_header)
                    except ValueError:
                        pass
            return APIRateLimitError(retry_after=retry_after, endpoint=endpoint)

        return APIError(
            message=f"HTTP error: {exc}",
            status_code=status_code,
            endpoint=endpoint,
        )

    # Handle requests-related exceptions
    if isinstance(exc, requests.exceptions.RequestException):
        return APIError(
            message=f"Request error: {exc}",
            endpoint=endpoint,
        )

    # Return original exception if it can't be converted
    return exc


def handle_api_errors(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
    """Decorator to handle common API errors with consistent behavior.

    This decorator wraps API-calling functions and provides:
    - Detection and conversion of common network exceptions (timeout, connection errors)
    - Consistent error logging
    - Conversion of exceptions to empty DataFrames for recoverable errors
    - Re-raising of critical errors (ValidationError, EntityNotFoundError)

    The decorator automatically converts these exception types:
    - requests.exceptions.Timeout -> APITimeoutError
    - requests.exceptions.ConnectionError -> APIError
    - requests.exceptions.HTTPError (429) -> APIRateLimitError
    - requests.exceptions.HTTPError (other) -> APIError
    - socket.timeout -> APITimeoutError

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
        except APIRateLimitError as e:
            log_error(
                f"API rate limit exceeded in {func.__name__}",
                {"retry_after": e.retry_after, "endpoint": e.endpoint},
            )
            return pd.DataFrame()
        except APIError as e:
            log_error(
                f"API error in {func.__name__}",
                {"status": e.status_code, "endpoint": e.endpoint},
            )
            return pd.DataFrame()
        except NBADataError:
            # Re-raise NBADataError subclasses that aren't API errors
            # (e.g., ValidationError, PlayerNotFoundError)
            raise
        except (requests.exceptions.Timeout, socket.timeout) as e:
            # Convert to custom exception and handle
            converted = convert_exception(e, endpoint=func.__name__)
            log_error(
                f"API timeout in {func.__name__}",
                {"error": str(e)},
            )
            return pd.DataFrame()
        except requests.exceptions.HTTPError as e:
            # Convert to custom exception and handle
            converted = convert_exception(e, endpoint=func.__name__)
            if isinstance(converted, APIRateLimitError):
                log_error(
                    f"API rate limit exceeded in {func.__name__}",
                    {"retry_after": converted.retry_after},
                )
            else:
                log_error(
                    f"HTTP error in {func.__name__}",
                    {"status": getattr(converted, "status_code", None), "error": str(e)},
                )
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            log_error(
                f"Request error in {func.__name__}",
                {"error": str(e)},
            )
            return pd.DataFrame()
        except Exception as e:
            log_error(f"Unexpected error in {func.__name__}: {e}")
            return pd.DataFrame()

    return wrapper


@contextmanager
def api_error_handler(
    context: Optional[dict] = None,
    reraise: bool = False,
) -> Generator[None, None, None]:
    """Context manager for handling API errors with consistent behavior.

    This context manager provides an alternative to the @handle_api_errors
    decorator for cases where you need more control over error handling.

    It provides:
    - Detection and conversion of common network exceptions
    - Consistent error logging with optional context
    - Option to re-raise exceptions after logging

    Args:
        context: Optional dictionary of contextual information for logging
        reraise: If True, re-raises the exception after logging. Default is False.

    Example:
        from lib.helpers.error_handling import api_error_handler

        with api_error_handler(context={"player_id": 12345}):
            result = api_endpoint.get_data()

        # With re-raising:
        try:
            with api_error_handler(context={"player_id": 12345}, reraise=True):
                result = api_endpoint.get_data()
        except APIError:
            # Handle error
            pass
    """
    try:
        yield
    except NBADataError:
        # Always re-raise NBADataError subclasses
        raise
    except (requests.exceptions.Timeout, socket.timeout) as e:
        converted = convert_exception(e)
        log_error("API timeout", context)
        if reraise:
            raise converted from e
    except requests.exceptions.HTTPError as e:
        converted = convert_exception(e)
        if isinstance(converted, APIRateLimitError):
            log_error("API rate limit exceeded", context)
        else:
            log_error(f"HTTP error: {e}", context)
        if reraise:
            raise converted from e
    except requests.exceptions.RequestException as e:
        converted = convert_exception(e)
        log_error(f"Request error: {e}", context)
        if reraise:
            raise converted from e
    except Exception as e:
        log_error(f"Unexpected error: {e}", context)
        if reraise:
            raise


def safe_api_call(
    func: Callable[..., T],
    *args,
    default: T = None,
    context: Optional[dict] = None,
    **kwargs,
) -> T:
    """Execute an API call with error handling and logging.

    This function provides a consistent way to make API calls with
    proper error handling, exception conversion, and logging.

    It automatically detects and converts common network exceptions:
    - requests.exceptions.Timeout -> APITimeoutError
    - requests.exceptions.ConnectionError -> APIError
    - requests.exceptions.HTTPError (429) -> APIRateLimitError
    - requests.exceptions.HTTPError (other) -> APIError
    - socket.timeout -> APITimeoutError

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
    func_name = getattr(func, "__name__", str(func))
    log_context = {"function": func_name}
    if context:
        log_context.update(context)

    try:
        return func(*args, **kwargs)
    except NBADataError:
        # Re-raise NBADataError subclasses
        raise
    except (requests.exceptions.Timeout, socket.timeout) as e:
        log_error("API timeout", log_context)
        return default
    except requests.exceptions.HTTPError as e:
        converted = convert_exception(e, endpoint=func_name)
        if isinstance(converted, APIRateLimitError):
            log_error("API rate limit exceeded", log_context)
        else:
            log_error(f"HTTP error: {e}", log_context)
        return default
    except requests.exceptions.RequestException as e:
        log_error(f"Request error: {e}", log_context)
        return default
    except Exception as e:
        log_error(f"API call failed: {e}", log_context)
        return default
