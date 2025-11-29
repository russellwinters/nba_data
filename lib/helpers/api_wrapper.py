"""Common API endpoint wrapper decorator with timeouts, retries, and error logging.

This module provides a decorator for API endpoint wrappers that handles:
- Configurable timeouts
- Automatic retries with exponential backoff
- Consistent error logging using the project's logging utilities

The decorator is designed to work with functions that make NBA API calls and
return pandas DataFrames, following the patterns established in the codebase.

Usage:
    from lib.helpers.api_wrapper import api_endpoint

    @api_endpoint(timeout=30, max_retries=3, retry_delay=1.0)
    def fetch_player_data(player_id: int) -> pd.DataFrame:
        # API call that might fail
        return df

    # Or with defaults:
    @api_endpoint()
    def fetch_team_data(team_id: str) -> pd.DataFrame:
        return df
"""

import functools
import socket
import time
from typing import Callable, Optional

import pandas as pd
import requests

from lib.helpers.error_handling import log_error, log_warning, log_info
from lib.helpers.exceptions import (
    APIError,
    APIRateLimitError,
    APITimeoutError,
    NBADataError,
)

# Default configuration values
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_BACKOFF_FACTOR = 2.0
DEFAULT_MAX_RETRY_DELAY = 60.0


def api_endpoint(
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
    on_error: str = "empty_dataframe",
) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """Decorator for API endpoint wrappers with timeout, retry, and error handling.

    This decorator provides a consistent pattern for wrapping NBA API calls with:
    - Configurable timeout handling
    - Automatic retries with exponential backoff for transient errors
    - Consistent error logging using the project's logging utilities
    - Graceful degradation (returns empty DataFrame on failure by default)

    The decorator handles the following exception types:
    - Timeout errors (requests.exceptions.Timeout, socket.timeout)
    - Connection errors (requests.exceptions.ConnectionError)
    - HTTP errors including rate limiting (requests.exceptions.HTTPError)
    - General request errors (requests.exceptions.RequestException)

    Retries are performed for transient errors (timeouts, connection errors,
    rate limits). Non-transient errors (ValidationError, EntityNotFoundError)
    are re-raised immediately.

    Args:
        timeout: Request timeout in seconds. Note: This is informational for logging;
                 the actual timeout should be passed to the underlying API call.
        max_retries: Maximum number of retry attempts for transient errors.
                     Set to 0 to disable retries.
        retry_delay: Initial delay between retries in seconds.
        backoff_factor: Multiplier for exponential backoff. Each retry waits
                        retry_delay * (backoff_factor ** attempt) seconds.
        max_retry_delay: Maximum delay between retries in seconds.
        on_error: Behavior when all retries are exhausted:
                  - "empty_dataframe": Return an empty pandas DataFrame (default)
                  - "raise": Re-raise the last exception
                  - "none": Return None

    Returns:
        Decorated function with timeout, retry, and error handling.

    Example:
        @api_endpoint(timeout=30, max_retries=3, retry_delay=1.0)
        def fetch_player_stats(player_id: int) -> pd.DataFrame:
            stats = playercareerstats.PlayerCareerStats(
                player_id=player_id,
                timeout=30
            )
            return stats.get_data_frames()[0]

        # With custom error handling:
        @api_endpoint(max_retries=5, on_error="raise")
        def fetch_critical_data(game_id: str) -> pd.DataFrame:
            # Raises exception if all retries fail
            return api_call()
    """

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> pd.DataFrame:
            last_exception: Optional[Exception] = None
            attempts = 0
            current_delay = retry_delay

            while attempts <= max_retries:
                try:
                    return func(*args, **kwargs)

                except NBADataError as e:
                    # Non-retryable errors: ValidationError, EntityNotFoundError, etc.
                    # These represent programming errors or missing data that won't
                    # succeed on retry - re-raise them immediately
                    # 
                    # Retryable errors: APITimeoutError, APIRateLimitError, APIError
                    # These may be transient network/server issues that can succeed on retry
                    is_retryable = isinstance(e, (APITimeoutError, APIRateLimitError, APIError))
                    if not is_retryable:
                        raise
                    # Continue to retry logic for API errors
                    last_exception = e
                    _log_retry_error(func.__name__, e, attempts, max_retries)

                except (requests.exceptions.Timeout, socket.timeout) as e:
                    last_exception = APITimeoutError(
                        timeout_seconds=timeout,
                        endpoint=func.__name__,
                    )
                    _log_retry_error(func.__name__, e, attempts, max_retries)

                except requests.exceptions.HTTPError as e:
                    response = getattr(e, "response", None)
                    status_code = getattr(response, "status_code", None) if response else None

                    if status_code == 429:
                        # Rate limit - extract retry-after if available
                        retry_after = None
                        if response is not None:
                            retry_after_header = response.headers.get("Retry-After")
                            if retry_after_header:
                                try:
                                    retry_after = int(retry_after_header)
                                except ValueError:
                                    pass
                        last_exception = APIRateLimitError(
                            retry_after=retry_after,
                            endpoint=func.__name__,
                        )
                        # Use server-specified retry delay if available
                        if retry_after is not None:
                            current_delay = min(retry_after, max_retry_delay)
                    else:
                        last_exception = APIError(
                            message=f"HTTP error: {e}",
                            status_code=status_code,
                            endpoint=func.__name__,
                        )
                    _log_retry_error(func.__name__, e, attempts, max_retries)

                except requests.exceptions.ConnectionError as e:
                    last_exception = APIError(
                        message=f"Connection error: {e}",
                        endpoint=func.__name__,
                    )
                    _log_retry_error(func.__name__, e, attempts, max_retries)

                except requests.exceptions.RequestException as e:
                    last_exception = APIError(
                        message=f"Request error: {e}",
                        endpoint=func.__name__,
                    )
                    _log_retry_error(func.__name__, e, attempts, max_retries)

                except Exception as e:
                    # Unexpected errors - log and don't retry
                    log_error(
                        f"Unexpected error in {func.__name__}",
                        {"error": str(e), "type": type(e).__name__},
                    )
                    last_exception = e
                    break

                # Check if we should retry
                attempts += 1
                if attempts <= max_retries:
                    log_info(
                        f"Retrying {func.__name__}",
                        {"attempt": attempts, "delay": current_delay},
                    )
                    time.sleep(current_delay)
                    # Apply exponential backoff
                    current_delay = min(current_delay * backoff_factor, max_retry_delay)

            # All retries exhausted
            log_error(
                f"All retries exhausted for {func.__name__}",
                {"max_retries": max_retries},
            )

            if on_error == "raise":
                if last_exception is not None:
                    raise last_exception
                raise APIError(f"Unknown error in {func.__name__}")
            elif on_error == "none":
                return None
            else:
                # Default: return empty DataFrame
                return pd.DataFrame()

        return wrapper

    return decorator


def _log_retry_error(
    func_name: str,
    error: Exception,
    attempt: int,
    max_retries: int,
) -> None:
    """Log an error during retry attempts.

    Args:
        func_name: Name of the function being retried
        error: The exception that occurred
        attempt: Current attempt number (0-indexed)
        max_retries: Maximum number of retries allowed
    """
    remaining = max_retries - attempt
    context = {
        "error": str(error),
        "attempt": attempt + 1,
        "remaining_retries": remaining,
    }

    if remaining > 0:
        log_warning(f"Transient error in {func_name}, will retry", context)
    else:
        log_error(f"Final attempt failed for {func_name}", context)
