"""Tests for lib/helpers/exceptions.py module."""

import pytest

from lib.helpers.exceptions import (
    APIError,
    APIRateLimitError,
    APITimeoutError,
    EntityNotFoundError,
    GameNotFoundError,
    NBADataError,
    PlayerNotFoundError,
    TeamNotFoundError,
    ValidationError,
)


class TestNBADataError:
    """Tests for the base NBADataError exception."""

    def test_nba_data_error_default_message(self):
        """Test default error message."""
        error = NBADataError()
        assert error.message == "An error occurred in nba_data"
        assert str(error) == "An error occurred in nba_data"

    def test_nba_data_error_custom_message(self):
        """Test custom error message."""
        error = NBADataError("Custom error message")
        assert error.message == "Custom error message"
        assert str(error) == "Custom error message"

    def test_nba_data_error_is_exception(self):
        """Test that NBADataError is an Exception."""
        error = NBADataError()
        assert isinstance(error, Exception)

    def test_nba_data_error_can_be_raised_and_caught(self):
        """Test that NBADataError can be raised and caught."""
        with pytest.raises(NBADataError) as exc_info:
            raise NBADataError("Test error")
        assert "Test error" in str(exc_info.value)


class TestEntityNotFoundError:
    """Tests for the EntityNotFoundError exception."""

    def test_entity_not_found_error_attributes(self):
        """Test entity_type and entity_id attributes."""
        error = EntityNotFoundError("player", 12345)
        assert error.entity_type == "player"
        assert error.entity_id == 12345

    def test_entity_not_found_error_default_message(self):
        """Test default error message formatting."""
        error = EntityNotFoundError("team", "LAL")
        assert "Team not found: 'LAL'" in str(error)

    def test_entity_not_found_error_custom_message(self):
        """Test custom error message."""
        error = EntityNotFoundError("game", "123", message="Custom message")
        assert str(error) == "Custom message"

    def test_entity_not_found_error_inheritance(self):
        """Test that EntityNotFoundError inherits from NBADataError."""
        error = EntityNotFoundError("player", 123)
        assert isinstance(error, NBADataError)
        assert isinstance(error, Exception)


class TestPlayerNotFoundError:
    """Tests for the PlayerNotFoundError exception."""

    def test_player_not_found_error_with_id(self):
        """Test PlayerNotFoundError with player ID."""
        error = PlayerNotFoundError(2544)
        assert error.player_id == 2544
        assert error.entity_type == "player"
        assert error.entity_id == 2544
        assert "Player not found: 2544" in str(error)

    def test_player_not_found_error_with_name(self):
        """Test PlayerNotFoundError with player name."""
        error = PlayerNotFoundError("LeBron James")
        assert error.player_id == "LeBron James"
        assert "Player not found: 'LeBron James'" in str(error)

    def test_player_not_found_error_custom_message(self):
        """Test PlayerNotFoundError with custom message."""
        error = PlayerNotFoundError(123, message="Player 123 does not exist")
        assert str(error) == "Player 123 does not exist"

    def test_player_not_found_error_inheritance(self):
        """Test that PlayerNotFoundError inherits from EntityNotFoundError."""
        error = PlayerNotFoundError(123)
        assert isinstance(error, EntityNotFoundError)
        assert isinstance(error, NBADataError)


class TestTeamNotFoundError:
    """Tests for the TeamNotFoundError exception."""

    def test_team_not_found_error_with_id(self):
        """Test TeamNotFoundError with team ID."""
        error = TeamNotFoundError(1610612747)
        assert error.team_id == 1610612747
        assert error.entity_type == "team"
        assert "Team not found: 1610612747" in str(error)

    def test_team_not_found_error_with_abbreviation(self):
        """Test TeamNotFoundError with team abbreviation."""
        error = TeamNotFoundError("XYZ")
        assert error.team_id == "XYZ"
        assert "Team not found: 'XYZ'" in str(error)

    def test_team_not_found_error_custom_message(self):
        """Test TeamNotFoundError with custom message."""
        error = TeamNotFoundError("LAL", message="Lakers not found")
        assert str(error) == "Lakers not found"

    def test_team_not_found_error_inheritance(self):
        """Test that TeamNotFoundError inherits from EntityNotFoundError."""
        error = TeamNotFoundError("LAL")
        assert isinstance(error, EntityNotFoundError)
        assert isinstance(error, NBADataError)


class TestGameNotFoundError:
    """Tests for the GameNotFoundError exception."""

    def test_game_not_found_error_with_id(self):
        """Test GameNotFoundError with game ID."""
        error = GameNotFoundError("0022400123")
        assert error.game_id == "0022400123"
        assert error.entity_type == "game"
        assert "Game not found: '0022400123'" in str(error)

    def test_game_not_found_error_custom_message(self):
        """Test GameNotFoundError with custom message."""
        error = GameNotFoundError("123", message="Game 123 not found")
        assert str(error) == "Game 123 not found"

    def test_game_not_found_error_inheritance(self):
        """Test that GameNotFoundError inherits from EntityNotFoundError."""
        error = GameNotFoundError("123")
        assert isinstance(error, EntityNotFoundError)
        assert isinstance(error, NBADataError)


class TestAPIError:
    """Tests for the APIError exception."""

    def test_api_error_default_message(self):
        """Test default error message."""
        error = APIError()
        assert "NBA API error" in str(error)

    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        error = APIError(message="API failed", status_code=500)
        assert error.status_code == 500
        assert "(status: 500)" in str(error)

    def test_api_error_with_endpoint(self):
        """Test APIError with endpoint."""
        error = APIError(message="Request failed", endpoint="player_stats")
        assert error.endpoint == "player_stats"
        assert "[endpoint: player_stats]" in str(error)

    def test_api_error_with_all_attributes(self):
        """Test APIError with all attributes."""
        error = APIError(
            message="Server error",
            status_code=503,
            endpoint="team_games",
        )
        assert error.status_code == 503
        assert error.endpoint == "team_games"
        assert "(status: 503)" in str(error)
        assert "[endpoint: team_games]" in str(error)

    def test_api_error_inheritance(self):
        """Test that APIError inherits from NBADataError."""
        error = APIError()
        assert isinstance(error, NBADataError)
        assert isinstance(error, Exception)


class TestAPITimeoutError:
    """Tests for the APITimeoutError exception."""

    def test_api_timeout_error_default(self):
        """Test default timeout error."""
        error = APITimeoutError()
        assert error.timeout_seconds is None
        assert "API request timed out" in str(error)

    def test_api_timeout_error_with_seconds(self):
        """Test timeout error with seconds."""
        error = APITimeoutError(timeout_seconds=30)
        assert error.timeout_seconds == 30
        assert "after 30s" in str(error)

    def test_api_timeout_error_with_endpoint(self):
        """Test timeout error with endpoint."""
        error = APITimeoutError(timeout_seconds=60, endpoint="player_games")
        assert error.timeout_seconds == 60
        assert error.endpoint == "player_games"
        assert "[endpoint: player_games]" in str(error)

    def test_api_timeout_error_inheritance(self):
        """Test that APITimeoutError inherits from APIError."""
        error = APITimeoutError()
        assert isinstance(error, APIError)
        assert isinstance(error, NBADataError)


class TestAPIRateLimitError:
    """Tests for the APIRateLimitError exception."""

    def test_api_rate_limit_error_default(self):
        """Test default rate limit error."""
        error = APIRateLimitError()
        assert error.retry_after is None
        assert error.status_code == 429
        assert "API rate limit exceeded" in str(error)

    def test_api_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after."""
        error = APIRateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert "(retry after 60s)" in str(error)

    def test_api_rate_limit_error_with_endpoint(self):
        """Test rate limit error with endpoint."""
        error = APIRateLimitError(retry_after=30, endpoint="boxscores")
        assert error.retry_after == 30
        assert error.endpoint == "boxscores"
        assert "[endpoint: boxscores]" in str(error)

    def test_api_rate_limit_error_inheritance(self):
        """Test that APIRateLimitError inherits from APIError."""
        error = APIRateLimitError()
        assert isinstance(error, APIError)
        assert isinstance(error, NBADataError)


class TestValidationError:
    """Tests for the ValidationError exception."""

    def test_validation_error_basic(self):
        """Test basic validation error."""
        error = ValidationError(parameter_name="player_id")
        assert error.parameter_name == "player_id"
        assert "Invalid value for 'player_id'" in str(error)

    def test_validation_error_with_value(self):
        """Test validation error with parameter value."""
        error = ValidationError(
            parameter_name="season",
            parameter_value="invalid",
        )
        assert error.parameter_value == "invalid"
        assert "'invalid'" in str(error)

    def test_validation_error_with_expected(self):
        """Test validation error with expected description."""
        error = ValidationError(
            parameter_name="team_id",
            parameter_value=-1,
            expected="a positive integer",
        )
        assert error.expected == "a positive integer"
        assert "Expected: a positive integer" in str(error)

    def test_validation_error_custom_message(self):
        """Test validation error with custom message."""
        error = ValidationError(
            parameter_name="date",
            message="Custom validation message",
        )
        assert str(error) == "Custom validation message"

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from NBADataError."""
        error = ValidationError(parameter_name="test")
        assert isinstance(error, NBADataError)
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    """Tests for exception hierarchy and catching behavior."""

    def test_catch_all_nba_errors(self):
        """Test that all custom exceptions can be caught with NBADataError."""
        exceptions = [
            NBADataError(),
            EntityNotFoundError("test", 1),
            PlayerNotFoundError(123),
            TeamNotFoundError("LAL"),
            GameNotFoundError("0022400123"),
            APIError(),
            APITimeoutError(),
            APIRateLimitError(),
            ValidationError(parameter_name="test"),
        ]

        for exc in exceptions:
            with pytest.raises(NBADataError):
                raise exc

    def test_catch_entity_errors(self):
        """Test that entity errors can be caught with EntityNotFoundError."""
        exceptions = [
            PlayerNotFoundError(123),
            TeamNotFoundError("LAL"),
            GameNotFoundError("0022400123"),
        ]

        for exc in exceptions:
            with pytest.raises(EntityNotFoundError):
                raise exc

    def test_catch_api_errors(self):
        """Test that API errors can be caught with APIError."""
        exceptions = [
            APITimeoutError(),
            APIRateLimitError(),
        ]

        for exc in exceptions:
            with pytest.raises(APIError):
                raise exc
