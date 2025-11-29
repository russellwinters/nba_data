"""Tests for lib/helpers/api_wrapper.py module."""

import socket
import time
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from lib.helpers.api_wrapper import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_RETRY_DELAY,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    _log_retry_error,
    api_endpoint,
)
from lib.helpers.exceptions import (
    APIError,
    APIRateLimitError,
    APITimeoutError,
    PlayerNotFoundError,
    ValidationError,
)


class TestApiEndpointDefaults:
    """Tests for default values in api_endpoint decorator."""

    def test_default_timeout(self):
        """Test default timeout value."""
        assert DEFAULT_TIMEOUT == 30

    def test_default_max_retries(self):
        """Test default max retries value."""
        assert DEFAULT_MAX_RETRIES == 3

    def test_default_retry_delay(self):
        """Test default retry delay value."""
        assert DEFAULT_RETRY_DELAY == 1.0

    def test_default_backoff_factor(self):
        """Test default backoff factor value."""
        assert DEFAULT_BACKOFF_FACTOR == 2.0

    def test_default_max_retry_delay(self):
        """Test default max retry delay value."""
        assert DEFAULT_MAX_RETRY_DELAY == 60.0


class TestApiEndpointSuccess:
    """Tests for successful api_endpoint decorated function calls."""

    def test_api_endpoint_returns_dataframe(self):
        """Test that decorated function returns DataFrame on success."""
        @api_endpoint()
        def fetch_data():
            return pd.DataFrame({"col": [1, 2, 3]})

        result = fetch_data()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_api_endpoint_preserves_function_name(self):
        """Test that decorator preserves function metadata."""
        @api_endpoint()
        def my_fetch_function():
            """My docstring."""
            return pd.DataFrame()

        assert my_fetch_function.__name__ == "my_fetch_function"
        assert my_fetch_function.__doc__ == "My docstring."

    def test_api_endpoint_passes_arguments(self):
        """Test that decorated function receives arguments correctly."""
        @api_endpoint()
        def fetch_with_args(player_id, season=None):
            return pd.DataFrame({"player_id": [player_id], "season": [season]})

        result = fetch_with_args(123, season="2023-24")
        assert result["player_id"].iloc[0] == 123
        assert result["season"].iloc[0] == "2023-24"


class TestApiEndpointRetryBehavior:
    """Tests for retry behavior of api_endpoint decorator."""

    def test_api_endpoint_retries_on_timeout(self, capsys):
        """Test that decorator retries on timeout errors."""
        call_count = 0

        @api_endpoint(max_retries=2, retry_delay=0.01)
        def flaky_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise requests.exceptions.Timeout("Timed out")
            return pd.DataFrame({"success": [True]})

        result = flaky_fetch()
        assert call_count == 2
        assert not result.empty

    def test_api_endpoint_retries_on_connection_error(self, capsys):
        """Test that decorator retries on connection errors."""
        call_count = 0

        @api_endpoint(max_retries=3, retry_delay=0.01)
        def connection_error_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.exceptions.ConnectionError("Connection refused")
            return pd.DataFrame({"success": [True]})

        result = connection_error_fetch()
        assert call_count == 3
        assert not result.empty

    def test_api_endpoint_retries_on_rate_limit(self, capsys):
        """Test that decorator retries on rate limit errors."""
        call_count = 0

        @api_endpoint(max_retries=2, retry_delay=0.01)
        def rate_limited_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                response = MagicMock()
                response.status_code = 429
                response.headers = {}
                raise requests.exceptions.HTTPError(response=response)
            return pd.DataFrame({"success": [True]})

        result = rate_limited_fetch()
        assert call_count == 2
        assert not result.empty

    def test_api_endpoint_respects_max_retries(self, capsys):
        """Test that decorator stops after max_retries."""
        call_count = 0

        @api_endpoint(max_retries=2, retry_delay=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise requests.exceptions.Timeout("Always times out")

        result = always_fails()
        # Initial call + 2 retries = 3 total calls
        assert call_count == 3
        assert result.empty

    def test_api_endpoint_no_retries_when_zero(self):
        """Test that max_retries=0 disables retries."""
        call_count = 0

        @api_endpoint(max_retries=0)
        def no_retry_fetch():
            nonlocal call_count
            call_count += 1
            raise requests.exceptions.Timeout("Timed out")

        result = no_retry_fetch()
        assert call_count == 1
        assert result.empty


class TestApiEndpointNonRetryableErrors:
    """Tests for non-retryable errors in api_endpoint decorator."""

    def test_api_endpoint_validation_error_not_retried(self):
        """Test that ValidationError is raised immediately without retries."""
        call_count = 0

        @api_endpoint(max_retries=3)
        def validation_error_fetch():
            nonlocal call_count
            call_count += 1
            raise ValidationError(parameter_name="player_id")

        with pytest.raises(ValidationError):
            validation_error_fetch()

        # Should only be called once
        assert call_count == 1

    def test_api_endpoint_entity_not_found_not_retried(self):
        """Test that EntityNotFoundError is raised immediately without retries."""
        call_count = 0

        @api_endpoint(max_retries=3)
        def not_found_fetch():
            nonlocal call_count
            call_count += 1
            raise PlayerNotFoundError(12345)

        with pytest.raises(PlayerNotFoundError):
            not_found_fetch()

        assert call_count == 1


class TestApiEndpointOnErrorBehavior:
    """Tests for on_error parameter behavior."""

    def test_api_endpoint_on_error_empty_dataframe(self, capsys):
        """Test on_error='empty_dataframe' returns empty DataFrame."""
        @api_endpoint(max_retries=0, on_error="empty_dataframe")
        def error_fetch():
            raise requests.exceptions.Timeout("Timed out")

        result = error_fetch()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_api_endpoint_on_error_raise(self):
        """Test on_error='raise' re-raises the exception."""
        @api_endpoint(max_retries=0, on_error="raise")
        def error_fetch():
            raise requests.exceptions.Timeout("Timed out")

        with pytest.raises(APITimeoutError):
            error_fetch()

    def test_api_endpoint_on_error_none(self):
        """Test on_error='none' returns None."""
        @api_endpoint(max_retries=0, on_error="none")
        def error_fetch():
            raise requests.exceptions.Timeout("Timed out")

        result = error_fetch()
        assert result is None


class TestApiEndpointExceptionConversion:
    """Tests for exception conversion in api_endpoint decorator."""

    def test_api_endpoint_converts_timeout_to_api_timeout_error(self):
        """Test that requests.Timeout is converted to APITimeoutError."""
        @api_endpoint(max_retries=0, on_error="raise")
        def timeout_fetch():
            raise requests.exceptions.Timeout("Timed out")

        with pytest.raises(APITimeoutError):
            timeout_fetch()

    def test_api_endpoint_converts_socket_timeout(self):
        """Test that socket.timeout is converted to APITimeoutError."""
        @api_endpoint(max_retries=0, on_error="raise")
        def socket_timeout_fetch():
            raise socket.timeout("Socket timed out")

        with pytest.raises(APITimeoutError):
            socket_timeout_fetch()

    def test_api_endpoint_converts_http_429_to_rate_limit_error(self):
        """Test that HTTP 429 is converted to APIRateLimitError."""
        @api_endpoint(max_retries=0, on_error="raise")
        def rate_limit_fetch():
            response = MagicMock()
            response.status_code = 429
            response.headers = {"Retry-After": "30"}
            raise requests.exceptions.HTTPError(response=response)

        with pytest.raises(APIRateLimitError) as exc_info:
            rate_limit_fetch()

        assert exc_info.value.retry_after == 30

    def test_api_endpoint_converts_http_error_to_api_error(self):
        """Test that other HTTP errors are converted to APIError."""
        @api_endpoint(max_retries=0, on_error="raise")
        def http_error_fetch():
            response = MagicMock()
            response.status_code = 500
            response.headers = {}
            raise requests.exceptions.HTTPError(response=response)

        with pytest.raises(APIError) as exc_info:
            http_error_fetch()

        assert exc_info.value.status_code == 500

    def test_api_endpoint_converts_connection_error(self):
        """Test that ConnectionError is converted to APIError."""
        @api_endpoint(max_retries=0, on_error="raise")
        def connection_error_fetch():
            raise requests.exceptions.ConnectionError("Connection refused")

        with pytest.raises(APIError):
            connection_error_fetch()


class TestApiEndpointUnexpectedErrors:
    """Tests for unexpected error handling in api_endpoint decorator."""

    def test_api_endpoint_unexpected_error_returns_empty_df(self, capsys):
        """Test that unexpected errors return empty DataFrame by default."""
        @api_endpoint(max_retries=0)
        def unexpected_error_fetch():
            raise RuntimeError("Unexpected error")

        result = unexpected_error_fetch()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

        captured = capsys.readouterr()
        assert "Unexpected error" in captured.out

    def test_api_endpoint_unexpected_error_no_retry(self):
        """Test that unexpected errors don't trigger retries."""
        call_count = 0

        @api_endpoint(max_retries=3)
        def unexpected_fetch():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Unexpected")

        unexpected_fetch()
        # Should only be called once (no retries for unexpected errors)
        assert call_count == 1


class TestApiEndpointCustomApiErrors:
    """Tests for custom API error handling in api_endpoint decorator."""

    def test_api_endpoint_retries_api_timeout_error(self, capsys):
        """Test that decorator retries on APITimeoutError."""
        call_count = 0

        @api_endpoint(max_retries=2, retry_delay=0.01)
        def custom_timeout_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APITimeoutError(timeout_seconds=30)
            return pd.DataFrame({"success": [True]})

        result = custom_timeout_fetch()
        assert call_count == 2
        assert not result.empty

    def test_api_endpoint_retries_api_rate_limit_error(self, capsys):
        """Test that decorator retries on APIRateLimitError."""
        call_count = 0

        @api_endpoint(max_retries=2, retry_delay=0.01)
        def custom_rate_limit_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIRateLimitError(retry_after=1)
            return pd.DataFrame({"success": [True]})

        result = custom_rate_limit_fetch()
        assert call_count == 2
        assert not result.empty

    def test_api_endpoint_retries_api_error(self, capsys):
        """Test that decorator retries on APIError."""
        call_count = 0

        @api_endpoint(max_retries=2, retry_delay=0.01)
        def custom_api_error_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIError(message="Server error", status_code=500)
            return pd.DataFrame({"success": [True]})

        result = custom_api_error_fetch()
        assert call_count == 2
        assert not result.empty


class TestLogRetryError:
    """Tests for the _log_retry_error helper function."""

    def test_log_retry_error_with_remaining_retries(self, capsys):
        """Test logging when retries remain."""
        error = requests.exceptions.Timeout("Timed out")
        _log_retry_error("test_func", error, attempt=0, max_retries=3)

        captured = capsys.readouterr()
        assert "Transient error" in captured.out
        assert "will retry" in captured.out
        assert "remaining_retries=3" in captured.out

    def test_log_retry_error_final_attempt(self, capsys):
        """Test logging on final attempt."""
        error = requests.exceptions.Timeout("Timed out")
        _log_retry_error("test_func", error, attempt=3, max_retries=3)

        captured = capsys.readouterr()
        assert "Final attempt failed" in captured.out
        assert "Error:" in captured.out


class TestApiEndpointBackoffBehavior:
    """Tests for exponential backoff behavior."""

    def test_api_endpoint_uses_rate_limit_retry_after(self, capsys):
        """Test that rate limit Retry-After header is respected."""
        call_count = 0
        call_times = []

        @api_endpoint(max_retries=1, retry_delay=0.01, max_retry_delay=0.05)
        def rate_limit_with_retry_after():
            nonlocal call_count
            call_count += 1
            call_times.append(time.time())
            if call_count < 2:
                response = MagicMock()
                response.status_code = 429
                response.headers = {"Retry-After": "0.02"}  # Very short for testing
                raise requests.exceptions.HTTPError(response=response)
            return pd.DataFrame({"success": [True]})

        result = rate_limit_with_retry_after()
        assert call_count == 2
        assert not result.empty


class TestApiEndpointWithCustomParameters:
    """Tests for api_endpoint with custom parameters."""

    def test_api_endpoint_with_custom_timeout(self):
        """Test decorator with custom timeout value."""
        @api_endpoint(timeout=60)
        def custom_timeout_fetch():
            return pd.DataFrame({"col": [1]})

        result = custom_timeout_fetch()
        assert not result.empty

    def test_api_endpoint_with_custom_retry_settings(self, capsys):
        """Test decorator with custom retry settings."""
        call_count = 0

        @api_endpoint(
            max_retries=5,
            retry_delay=0.01,
            backoff_factor=1.5,
            max_retry_delay=0.1,
        )
        def custom_retry_fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise requests.exceptions.Timeout("Timed out")
            return pd.DataFrame({"success": [True]})

        result = custom_retry_fetch()
        assert call_count == 4
        assert not result.empty
