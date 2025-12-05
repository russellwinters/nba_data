"""Tests for lib/helpers/error_handling.py module."""

import socket
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from lib.helpers.error_handling import (
    _format_log_message,
    api_error_handler,
    convert_exception,
    handle_api_errors,
    log_error,
    log_info,
    log_warning,
    safe_api_call,
    setup_logging,
)
from lib.helpers.exceptions import (
    APIError,
    APIRateLimitError,
    APITimeoutError,
    NBADataError,
    PlayerNotFoundError,
    ValidationError,
)


class TestFormatLogMessage:
    def test_format_log_message_no_context(self):
        result = _format_log_message("Test message")
        assert result == "Test message"

    def test_format_log_message_with_context(self):
        result = _format_log_message("Test message", {"key": "value"})
        assert "Test message" in result
        assert "key='value'" in result

    def test_format_log_message_with_multiple_context_items(self):
        result = _format_log_message("Error", {"player_id": 123, "season": "2023-24"})
        assert "Error" in result
        assert "player_id=123" in result
        assert "season='2023-24'" in result

    def test_format_log_message_with_numeric_values(self):
        result = _format_log_message("Stats", {"count": 42, "avg": 12.5})
        assert "count=42" in result
        assert "avg=12.5" in result


class TestLogFunctions:
    def test_log_error_prints_message(self, capsys):
        log_error("Test error message")
        captured = capsys.readouterr()
        assert "Error: Test error message" in captured.out

    def test_log_error_with_context(self, capsys):
        log_error("Failed to fetch", {"player_id": 123})
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Failed to fetch" in captured.out
        assert "player_id=123" in captured.out

    def test_log_warning_prints_message(self, capsys):
        log_warning("Test warning message")
        captured = capsys.readouterr()
        assert "Warning: Test warning message" in captured.out

    def test_log_warning_with_context(self, capsys):
        log_warning("No data found", {"team": "LAL"})
        captured = capsys.readouterr()
        assert "Warning:" in captured.out
        assert "No data found" in captured.out
        assert "team='LAL'" in captured.out

    def test_log_info_prints_message(self, capsys):
        log_info("Test info message")
        captured = capsys.readouterr()
        assert "Test info message" in captured.out
        assert "Info:" not in captured.out

    def test_log_info_with_context(self, capsys):
        log_info("Fetching data", {"endpoint": "player_stats"})
        captured = capsys.readouterr()
        assert "Fetching data" in captured.out
        assert "endpoint='player_stats'" in captured.out


class TestSetupLogging:
    def test_setup_logging_default(self):
        # Should not raise
        setup_logging()

    def test_setup_logging_with_custom_format(self):
        setup_logging(format_string="%(message)s")


class TestConvertException:
    def test_convert_timeout_exception(self):
        exc = requests.exceptions.Timeout("Request timed out")
        result = convert_exception(exc, endpoint="test_endpoint")
        assert isinstance(result, APITimeoutError)
        assert result.endpoint == "test_endpoint"

    def test_convert_socket_timeout(self):
        exc = socket.timeout("Socket timed out")
        result = convert_exception(exc, endpoint="socket_test")
        assert isinstance(result, APITimeoutError)
        assert result.endpoint == "socket_test"

    def test_convert_connection_error(self):
        exc = requests.exceptions.ConnectionError("Connection refused")
        result = convert_exception(exc, endpoint="connection_test")
        assert isinstance(result, APIError)
        assert result.endpoint == "connection_test"
        assert "Connection error" in result.message

    def test_convert_http_error_rate_limit(self):
        response = MagicMock()
        response.status_code = 429
        response.headers = {"Retry-After": "60"}
        exc = requests.exceptions.HTTPError(response=response)
        
        result = convert_exception(exc, endpoint="rate_limit_test")
        assert isinstance(result, APIRateLimitError)
        assert result.retry_after == 60
        assert result.endpoint == "rate_limit_test"

    def test_convert_http_error_other(self):
        response = MagicMock()
        response.status_code = 500
        response.headers = {}
        exc = requests.exceptions.HTTPError(response=response)
        
        result = convert_exception(exc, endpoint="server_error")
        assert isinstance(result, APIError)
        assert result.status_code == 500

    def test_convert_request_exception(self):
        exc = requests.exceptions.RequestException("Generic error")
        result = convert_exception(exc, endpoint="generic_test")
        assert isinstance(result, APIError)
        assert "Request error" in result.message

    def test_convert_unknown_exception_returns_original(self):
        exc = ValueError("Unknown error")
        result = convert_exception(exc, endpoint="unknown_test")
        assert result is exc


class TestHandleApiErrorsDecorator:
    def test_handle_api_errors_success(self):
        @handle_api_errors
        def successful_func():
            return pd.DataFrame({"col": [1, 2, 3]})

        result = successful_func()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_handle_api_errors_timeout_returns_empty_df(self, capsys):
        @handle_api_errors
        def timeout_func():
            raise APITimeoutError(timeout_seconds=30, endpoint="test")

        result = timeout_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

        captured = capsys.readouterr()
        assert "timeout" in captured.out.lower()

    def test_handle_api_errors_rate_limit_returns_empty_df(self, capsys):
        @handle_api_errors
        def rate_limit_func():
            raise APIRateLimitError(retry_after=60)

        result = rate_limit_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

        captured = capsys.readouterr()
        assert "rate limit" in captured.out.lower()

    def test_handle_api_errors_api_error_returns_empty_df(self, capsys):
        @handle_api_errors
        def api_error_func():
            raise APIError(message="Server error", status_code=500)

        result = api_error_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_api_errors_validation_error_reraises(self):
        @handle_api_errors
        def validation_func():
            raise ValidationError(parameter_name="test")

        with pytest.raises(ValidationError):
            validation_func()

    def test_handle_api_errors_entity_not_found_reraises(self):
        @handle_api_errors
        def not_found_func():
            raise PlayerNotFoundError(12345)

        with pytest.raises(PlayerNotFoundError):
            not_found_func()

    def test_handle_api_errors_requests_timeout(self, capsys):
        @handle_api_errors
        def native_timeout_func():
            raise requests.exceptions.Timeout("Connection timed out")

        result = native_timeout_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_api_errors_socket_timeout(self, capsys):
        @handle_api_errors
        def socket_timeout_func():
            raise socket.timeout("Socket timed out")

        result = socket_timeout_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_api_errors_http_error(self, capsys):
        @handle_api_errors
        def http_error_func():
            response = MagicMock()
            response.status_code = 500
            response.headers = {}
            raise requests.exceptions.HTTPError(response=response)

        result = http_error_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_api_errors_request_exception(self, capsys):
        @handle_api_errors
        def request_error_func():
            raise requests.exceptions.RequestException("Request failed")

        result = request_error_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_api_errors_unexpected_exception(self, capsys):
        @handle_api_errors
        def unexpected_error_func():
            raise RuntimeError("Unexpected error")

        result = unexpected_error_func()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

        captured = capsys.readouterr()
        assert "Unexpected error" in captured.out

    def test_handle_api_errors_preserves_function_name(self):
        @handle_api_errors
        def my_function():
            """My docstring."""
            return pd.DataFrame()

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."


class TestApiErrorHandlerContextManager:
    def test_api_error_handler_success(self):
        result = None
        with api_error_handler():
            result = "success"
        assert result == "success"

    def test_api_error_handler_timeout_logged(self, capsys):
        with api_error_handler(context={"player_id": 123}):
            raise requests.exceptions.Timeout("Timed out")

        captured = capsys.readouterr()
        assert "timeout" in captured.out.lower()
        assert "player_id=123" in captured.out

    def test_api_error_handler_reraise_timeout(self):
        with pytest.raises(APITimeoutError):
            with api_error_handler(reraise=True):
                raise requests.exceptions.Timeout("Timed out")

    def test_api_error_handler_http_error_logged(self, capsys):
        response = MagicMock()
        response.status_code = 500
        response.headers = {}

        with api_error_handler():
            raise requests.exceptions.HTTPError(response=response)

        captured = capsys.readouterr()
        assert "HTTP error" in captured.out

    def test_api_error_handler_rate_limit_logged(self, capsys):
        response = MagicMock()
        response.status_code = 429
        response.headers = {}

        with api_error_handler():
            raise requests.exceptions.HTTPError(response=response)

        captured = capsys.readouterr()
        assert "rate limit" in captured.out.lower()

    def test_api_error_handler_request_exception_logged(self, capsys):
        with api_error_handler():
            raise requests.exceptions.RequestException("Request failed")

        captured = capsys.readouterr()
        assert "Request error" in captured.out

    def test_api_error_handler_unexpected_exception_logged(self, capsys):
        with api_error_handler():
            raise RuntimeError("Unexpected")

        captured = capsys.readouterr()
        assert "Unexpected" in captured.out

    def test_api_error_handler_reraise_unexpected(self):
        with pytest.raises(RuntimeError):
            with api_error_handler(reraise=True):
                raise RuntimeError("Should reraise")

    def test_api_error_handler_nba_data_error_always_reraises(self):
        with pytest.raises(ValidationError):
            with api_error_handler(reraise=False):
                raise ValidationError(parameter_name="test")

    def test_api_error_handler_with_endpoint(self):
        with pytest.raises(APITimeoutError) as exc_info:
            with api_error_handler(reraise=True, endpoint="my_endpoint"):
                raise requests.exceptions.Timeout("Timed out")

        assert exc_info.value.endpoint == "my_endpoint"


class TestSafeApiCall:
    def test_safe_api_call_success(self):
        def success_func(x, y):
            return x + y

        result = safe_api_call(success_func, 1, 2)
        assert result == 3

    def test_safe_api_call_with_kwargs(self):
        def kwarg_func(x, multiplier=1):
            return x * multiplier

        result = safe_api_call(kwarg_func, 5, multiplier=3)
        assert result == 15

    def test_safe_api_call_timeout_returns_default(self, capsys):
        def timeout_func():
            raise requests.exceptions.Timeout("Timed out")

        result = safe_api_call(timeout_func, default=[])
        assert result == []

        captured = capsys.readouterr()
        assert "timeout" in captured.out.lower()

    def test_safe_api_call_http_error_returns_default(self, capsys):
        def http_error_func():
            response = MagicMock()
            response.status_code = 404
            response.headers = {}
            raise requests.exceptions.HTTPError(response=response)

        result = safe_api_call(http_error_func, default=None)
        assert result is None

    def test_safe_api_call_rate_limit_returns_default(self, capsys):
        def rate_limit_func():
            response = MagicMock()
            response.status_code = 429
            response.headers = {}
            raise requests.exceptions.HTTPError(response=response)

        result = safe_api_call(rate_limit_func, default="rate_limited")
        assert result == "rate_limited"

        captured = capsys.readouterr()
        assert "rate limit" in captured.out.lower()

    def test_safe_api_call_request_exception_returns_default(self, capsys):
        def request_error_func():
            raise requests.exceptions.RequestException("Connection error")

        result = safe_api_call(request_error_func, default={})
        assert result == {}

    def test_safe_api_call_generic_exception_returns_default(self, capsys):
        def generic_error_func():
            raise RuntimeError("Something went wrong")

        result = safe_api_call(generic_error_func, default=-1)
        assert result == -1

        captured = capsys.readouterr()
        assert "failed" in captured.out.lower()

    def test_safe_api_call_validation_error_reraises(self):
        def validation_error_func():
            raise ValidationError(parameter_name="test")

        with pytest.raises(ValidationError):
            safe_api_call(validation_error_func, default=None)

    def test_safe_api_call_with_context(self, capsys):
        def error_func():
            raise requests.exceptions.Timeout("Timed out")

        safe_api_call(
            error_func,
            default=None,
            context={"operation": "fetch_player", "player_id": 123},
        )

        captured = capsys.readouterr()
        assert "operation='fetch_player'" in captured.out
        assert "player_id=123" in captured.out

    def test_safe_api_call_default_is_none(self):
        def error_func():
            raise requests.exceptions.Timeout("Timed out")

        result = safe_api_call(error_func)
        assert result is None
