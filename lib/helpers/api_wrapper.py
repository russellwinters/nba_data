"""API endpoint wrapper with timeout, retry, and error logging support.

This module provides decorators and utilities for wrapping API endpoint calls
with consistent timeout handling, automatic retries with exponential backoff,
and integrated error logging.

The main decorator `api_endpoint_wrapper` can be applied to any function that
makes API calls, providing:
- Configurable timeout
- Configurable retry count with exponential backoff
- Automatic error logging via the error_handling module
- Integration with custom exception types

Example:
    from lib.helpers.api_wrapper import api_endpoint_wrapper

    @api_endpoint_wrapper(timeout=30, max_retries=3, backoff_factor=1.5)
    def fetch_player_data(player_id):
        # API call that might timeout or fail temporarily
        return api.get_player(player_id)

    # For functions returning DataFrames (common pattern in this codebase):
    @api_endpoint_wrapper(timeout=30, max_retries=3, return_empty_df_on_error=True)
    def fetch_player_stats(player_id):
        return api.get_stats(player_id)
"""

import functools
import random
import socket
import time
from typing import Any, Callable, Optional, TypeVar, Union

import pandas as pd
import requests

from lib.helpers.error_handling import log_error, log_warning, log_info
from lib.helpers.exceptions import (
    APIError,
    APIRateLimitError,
    APITimeoutError,
    NBADataError,
)

# Type variable for generic function return type
T = TypeVar("T")

# Default configuration values
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1.5
DEFAULT_INITIAL_DELAY = 1.0
DEFAULT_MAX_DELAY = 60.0
DEFAULT_JITTER = True


def _is_retryable_exception(exc: Exception) -> bool:
    """Determine if an exception is retryable.

    Some errors are transient and may succeed on retry (network issues,
    timeouts, rate limits). Others are permanent and should not be retried
    (invalid parameters, authentication errors).

    Args:
        exc: The exception to evaluate

    Returns:
        True if the exception is retryable, False otherwise
    """
    # Timeout errors are retryable
    if isinstance(exc, (requests.exceptions.Timeout, socket.timeout, APITimeoutError)):
        return True

    # Connection errors are retryable
    if isinstance(exc, requests.exceptions.ConnectionError):
        return True

    # Rate limit errors are retryable (after waiting)
    if isinstance(exc, APIRateLimitError):
        return True

    # HTTP errors may be retryable depending on status code
    if isinstance(exc, requests.exceptions.HTTPError):
        response = getattr(exc, "response", None)
        if response is not None:
            status_code = response.status_code
            # 429 (rate limit), 500s (server errors) are retryable
            if status_code == 429 or 500 <= status_code < 600:
                return True
        return False

    # Generic API errors may be retryable
    if isinstance(exc, APIError):
        if exc.status_code:
            # 429 (rate limit), 500s (server errors) are retryable
            if exc.status_code == 429 or 500 <= exc.status_code < 600:
                return True
        return False

    # Other request exceptions may be retryable
    if isinstance(exc, requests.exceptions.RequestException):
        return True

    # Non-retryable by default
    return False


def _calculate_delay(
    attempt: int,
    backoff_factor: float,
    initial_delay: float,
    max_delay: float,
    jitter: bool,
    rate_limit_retry_after: Optional[int] = None,
) -> float:
    """Calculate the delay before the next retry attempt.

    Uses exponential backoff with optional jitter to prevent thundering herd.

    Args:
        attempt: Current attempt number (0-indexed)
        backoff_factor: Multiplier for exponential backoff
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter to the delay
        rate_limit_retry_after: If provided, use this as minimum delay (from 429 response)

    Returns:
        Delay in seconds before next retry
    """
    # Calculate base delay with exponential backoff
    delay = initial_delay * (backoff_factor ** attempt)

    # Cap at max delay
    delay = min(delay, max_delay)

    # If rate limit retry-after is provided, use it as minimum
    if rate_limit_retry_after is not None:
        delay = max(delay, rate_limit_retry_after)

    # Add jitter to prevent thundering herd
    if jitter:
        # Add random jitter of 0-25% of the delay
        jitter_amount = delay * 0.25 * random.random()
        delay = delay + jitter_amount

    return delay


def _extract_retry_after(exc: Exception) -> Optional[int]:
    """Extract Retry-After header value from rate limit exceptions.

    Args:
        exc: The exception to examine

    Returns:
        Retry-After value in seconds, or None if not available
    """
    if isinstance(exc, APIRateLimitError):
        return exc.retry_after

    if isinstance(exc, requests.exceptions.HTTPError):
        response = getattr(exc, "response", None)
        if response is not None and response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
    return None


def api_endpoint_wrapper(
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    jitter: bool = DEFAULT_JITTER,
    return_empty_df_on_error: bool = False,
    log_retries: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for API endpoint wrappers with timeout, retry, and error handling.

    This decorator wraps functions that make API calls and provides:
    - Configurable timeout (passed to the wrapped function if it accepts it)
    - Automatic retries with exponential backoff for transient errors
    - Respect for Retry-After headers in rate limit responses
    - Consistent error logging
    - Optional return of empty DataFrame on final failure

    The decorator is designed to work with functions that either:
    1. Accept a `timeout` parameter (the timeout value will be passed)
    2. Do not accept a `timeout` parameter (timeout is not enforced by decorator)

    Note: The actual timeout enforcement depends on the underlying library
    (e.g., nba_api, requests) respecting the timeout parameter.

    Args:
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_factor: Multiplier for exponential backoff (default: 1.5)
        initial_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        jitter: Whether to add random jitter to delays (default: True)
        return_empty_df_on_error: Return empty DataFrame on final failure (default: False)
        log_retries: Whether to log retry attempts (default: True)

    Returns:
        Decorated function with retry and timeout behavior

    Example:
        @api_endpoint_wrapper(timeout=30, max_retries=3)
        def fetch_player_data(player_id, timeout=30):
            # The timeout parameter will be set by the decorator
            return api.get_player(player_id, timeout=timeout)

        @api_endpoint_wrapper(max_retries=5, return_empty_df_on_error=True)
        def fetch_stats():
            # Returns empty DataFrame if all retries fail
            return api.get_stats()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, pd.DataFrame]:
            # Inject timeout into kwargs if the function accepts it
            # Check if function signature accepts timeout
            import inspect
            sig = inspect.signature(func)
            if "timeout" in sig.parameters and "timeout" not in kwargs:
                kwargs["timeout"] = timeout

            last_exception: Optional[Exception] = None
            func_name = func.__name__

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except NBADataError as e:
                    # Check if it's a retryable API error
                    if not _is_retryable_exception(e):
                        # Non-retryable NBADataError, re-raise
                        raise

                    last_exception = e
                    if attempt < max_retries:
                        retry_after = _extract_retry_after(e)
                        delay = _calculate_delay(
                            attempt,
                            backoff_factor,
                            initial_delay,
                            max_delay,
                            jitter,
                            retry_after,
                        )
                        if log_retries:
                            log_warning(
                                f"Retry {attempt + 1}/{max_retries} for {func_name}",
                                {"error": str(e), "delay": f"{delay:.2f}s"},
                            )
                        time.sleep(delay)
                    else:
                        # Max retries exceeded
                        log_error(
                            f"Max retries ({max_retries}) exceeded for {func_name}",
                            {"error": str(e)},
                        )

                except (requests.exceptions.Timeout, socket.timeout) as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = _calculate_delay(
                            attempt,
                            backoff_factor,
                            initial_delay,
                            max_delay,
                            jitter,
                        )
                        if log_retries:
                            log_warning(
                                f"Timeout, retry {attempt + 1}/{max_retries} for {func_name}",
                                {"error": str(e), "delay": f"{delay:.2f}s"},
                            )
                        time.sleep(delay)
                    else:
                        log_error(
                            f"Max retries ({max_retries}) exceeded due to timeout for {func_name}",
                            {"error": str(e)},
                        )

                except requests.exceptions.HTTPError as e:
                    if not _is_retryable_exception(e):
                        # Non-retryable HTTP error
                        log_error(
                            f"Non-retryable HTTP error in {func_name}",
                            {"error": str(e)},
                        )
                        if return_empty_df_on_error:
                            return pd.DataFrame()
                        raise

                    last_exception = e
                    if attempt < max_retries:
                        retry_after = _extract_retry_after(e)
                        delay = _calculate_delay(
                            attempt,
                            backoff_factor,
                            initial_delay,
                            max_delay,
                            jitter,
                            retry_after,
                        )
                        if log_retries:
                            log_warning(
                                f"HTTP error, retry {attempt + 1}/{max_retries} for {func_name}",
                                {"error": str(e), "delay": f"{delay:.2f}s"},
                            )
                        time.sleep(delay)
                    else:
                        log_error(
                            f"Max retries ({max_retries}) exceeded for {func_name}",
                            {"error": str(e)},
                        )

                except requests.exceptions.RequestException as e:
                    if not _is_retryable_exception(e):
                        log_error(
                            f"Non-retryable request error in {func_name}",
                            {"error": str(e)},
                        )
                        if return_empty_df_on_error:
                            return pd.DataFrame()
                        raise

                    last_exception = e
                    if attempt < max_retries:
                        delay = _calculate_delay(
                            attempt,
                            backoff_factor,
                            initial_delay,
                            max_delay,
                            jitter,
                        )
                        if log_retries:
                            log_warning(
                                f"Request error, retry {attempt + 1}/{max_retries} for {func_name}",
                                {"error": str(e), "delay": f"{delay:.2f}s"},
                            )
                        time.sleep(delay)
                    else:
                        log_error(
                            f"Max retries ({max_retries}) exceeded for {func_name}",
                            {"error": str(e)},
                        )

                except Exception as e:
                    # Unexpected errors are not retried
                    log_error(
                        f"Unexpected error in {func_name}",
                        {"error": str(e)},
                    )
                    if return_empty_df_on_error:
                        return pd.DataFrame()
                    raise

            # All retries exhausted
            if return_empty_df_on_error:
                return pd.DataFrame()

            # Re-raise the last exception
            if last_exception is not None:
                raise last_exception

            # Should not reach here, but return empty DataFrame as fallback
            return pd.DataFrame() if return_empty_df_on_error else None

        return wrapper

    return decorator


def with_retry(
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    jitter: bool = DEFAULT_JITTER,
    retryable_exceptions: tuple = None,
    log_retries: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for adding retry logic to any function.

    This is a more general-purpose retry decorator that can be used for
    non-API functions that may fail transiently and benefit from retries.

    Unlike `api_endpoint_wrapper`, this decorator:
    - Does not inject timeout parameters
    - Uses a simpler exception handling model
    - Allows custom specification of retryable exceptions

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_factor: Multiplier for exponential backoff (default: 1.5)
        initial_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        jitter: Whether to add random jitter to delays (default: True)
        retryable_exceptions: Tuple of exception types to retry on.
            If None, uses default retryable exceptions.
        log_retries: Whether to log retry attempts (default: True)

    Returns:
        Decorated function with retry behavior

    Example:
        @with_retry(max_retries=3, retryable_exceptions=(ConnectionError, TimeoutError))
        def unstable_operation():
            # Operation that might fail
            pass
    """
    if retryable_exceptions is None:
        # Default retryable exceptions
        retryable_exceptions = (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            socket.timeout,
            APITimeoutError,
            APIRateLimitError,
        )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Optional[Exception] = None
            func_name = func.__name__

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = _calculate_delay(
                            attempt,
                            backoff_factor,
                            initial_delay,
                            max_delay,
                            jitter,
                        )
                        if log_retries:
                            log_warning(
                                f"Retry {attempt + 1}/{max_retries} for {func_name}",
                                {"error": str(e), "delay": f"{delay:.2f}s"},
                            )
                        time.sleep(delay)
                    else:
                        log_error(
                            f"Max retries ({max_retries}) exceeded for {func_name}",
                            {"error": str(e)},
                        )

            # All retries exhausted, re-raise last exception
            if last_exception is not None:
                raise last_exception

            # Should not reach here
            return None

        return wrapper

    return decorator
