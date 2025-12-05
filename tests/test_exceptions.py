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
    def test_nba_data_error_default_message(self):
        error = NBADataError()
        assert error.message == "An error occurred in nba_data"
        assert str(error) == "An error occurred in nba_data"

    def test_nba_data_error_custom_message(self):
        error = NBADataError("Custom error message")
        assert error.message == "Custom error message"
        assert str(error) == "Custom error message"

    def test_nba_data_error_is_exception(self):
        error = NBADataError()
        assert isinstance(error, Exception)

    def test_nba_data_error_can_be_raised_and_caught(self):
        with pytest.raises(NBADataError) as exc_info:
            raise NBADataError("Test error")
        assert "Test error" in str(exc_info.value)


class TestEntityNotFoundError:
    def test_entity_not_found_error_attributes(self):
        error = EntityNotFoundError("player", 12345)
        assert error.entity_type == "player"
        assert error.entity_id == 12345

    def test_entity_not_found_error_default_message(self):
        error = EntityNotFoundError("team", "LAL")
        assert "Team not found: 'LAL'" in str(error)

    def test_entity_not_found_error_custom_message(self):
        error = EntityNotFoundError("game", "123", message="Custom message")
        assert str(error) == "Custom message"

    def test_entity_not_found_error_inheritance(self):
        error = EntityNotFoundError("player", 123)
        assert isinstance(error, NBADataError)
        assert isinstance(error, Exception)


class TestPlayerNotFoundError:
    def test_player_not_found_error_with_id(self):
        error = PlayerNotFoundError(2544)
        assert error.player_id == 2544
        assert error.entity_type == "player"
        assert error.entity_id == 2544
        assert "Player not found: 2544" in str(error)

    def test_player_not_found_error_with_name(self):
        error = PlayerNotFoundError("LeBron James")
        assert error.player_id == "LeBron James"
        assert "Player not found: 'LeBron James'" in str(error)

    def test_player_not_found_error_custom_message(self):
        error = PlayerNotFoundError(123, message="Player 123 does not exist")
        assert str(error) == "Player 123 does not exist"

    def test_player_not_found_error_inheritance(self):
        error = PlayerNotFoundError(123)
        assert isinstance(error, EntityNotFoundError)
        assert isinstance(error, NBADataError)


class TestTeamNotFoundError:
    def test_team_not_found_error_with_id(self):
        error = TeamNotFoundError(1610612747)
        assert error.team_id == 1610612747
        assert error.entity_type == "team"
        assert "Team not found: 1610612747" in str(error)

    def test_team_not_found_error_with_abbreviation(self):
        error = TeamNotFoundError("XYZ")
        assert error.team_id == "XYZ"
        assert "Team not found: 'XYZ'" in str(error)

    def test_team_not_found_error_custom_message(self):
        error = TeamNotFoundError("LAL", message="Lakers not found")
        assert str(error) == "Lakers not found"

    def test_team_not_found_error_inheritance(self):
        error = TeamNotFoundError("LAL")
        assert isinstance(error, EntityNotFoundError)
        assert isinstance(error, NBADataError)


class TestGameNotFoundError:
    def test_game_not_found_error_with_id(self):
        error = GameNotFoundError("0022400123")
        assert error.game_id == "0022400123"
        assert error.entity_type == "game"
        assert "Game not found: '0022400123'" in str(error)

    def test_game_not_found_error_custom_message(self):
        error = GameNotFoundError("123", message="Game 123 not found")
        assert str(error) == "Game 123 not found"

    def test_game_not_found_error_inheritance(self):
        error = GameNotFoundError("123")
        assert isinstance(error, EntityNotFoundError)
        assert isinstance(error, NBADataError)


class TestAPIError:
    def test_api_error_default_message(self):
        error = APIError()
        assert "NBA API error" in str(error)

    def test_api_error_with_status_code(self):
        error = APIError(message="API failed", status_code=500)
        assert error.status_code == 500
        assert "(status: 500)" in str(error)

    def test_api_error_with_endpoint(self):
        error = APIError(message="Request failed", endpoint="player_stats")
        assert error.endpoint == "player_stats"
        assert "[endpoint: player_stats]" in str(error)

    def test_api_error_with_all_attributes(self):
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
        error = APIError()
        assert isinstance(error, NBADataError)
        assert isinstance(error, Exception)


class TestAPITimeoutError:
    def test_api_timeout_error_default(self):
        error = APITimeoutError()
        assert error.timeout_seconds is None
        assert "API request timed out" in str(error)

    def test_api_timeout_error_with_seconds(self):
        error = APITimeoutError(timeout_seconds=30)
        assert error.timeout_seconds == 30
        assert "after 30s" in str(error)

    def test_api_timeout_error_with_endpoint(self):
        error = APITimeoutError(timeout_seconds=60, endpoint="player_games")
        assert error.timeout_seconds == 60
        assert error.endpoint == "player_games"
        assert "[endpoint: player_games]" in str(error)

    def test_api_timeout_error_inheritance(self):
        error = APITimeoutError()
        assert isinstance(error, APIError)
        assert isinstance(error, NBADataError)

class TestAPIRateLimitError:
    def test_api_rate_limit_error_default(self):
        error = APIRateLimitError()
        assert error.retry_after is None
        assert error.status_code == 429
        assert "API rate limit exceeded" in str(error)

    def test_api_rate_limit_error_with_retry_after(self):
        error = APIRateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert "(retry after 60s)" in str(error)

    def test_api_rate_limit_error_with_endpoint(self):
        error = APIRateLimitError(retry_after=30, endpoint="boxscores")
        assert error.retry_after == 30
        assert error.endpoint == "boxscores"
        assert "[endpoint: boxscores]" in str(error)

    def test_api_rate_limit_error_inheritance(self):
        error = APIRateLimitError()
        assert isinstance(error, APIError)
        assert isinstance(error, NBADataError)


class TestValidationError:
    def test_validation_error_basic(self):
        error = ValidationError(parameter_name="player_id")
        assert error.parameter_name == "player_id"
        assert "Invalid value for 'player_id'" in str(error)

    def test_validation_error_with_value(self):
        error = ValidationError(
            parameter_name="season",
            parameter_value="invalid",
        )
        assert error.parameter_value == "invalid"
        assert "'invalid'" in str(error)

    def test_validation_error_with_expected(self):
        error = ValidationError(
            parameter_name="team_id",
            parameter_value=-1,
            expected="a positive integer",
        )
        assert error.expected == "a positive integer"
        assert "Expected: a positive integer" in str(error)

    def test_validation_error_custom_message(self):
        error = ValidationError(
            parameter_name="date",
            message="Custom validation message",
        )
        assert str(error) == "Custom validation message"

    def test_validation_error_inheritance(self):
        error = ValidationError(parameter_name="test")
        assert isinstance(error, NBADataError)
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    def test_catch_all_nba_errors(self):
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
        exceptions = [
            PlayerNotFoundError(123),
            TeamNotFoundError("LAL"),
            GameNotFoundError("0022400123"),
        ]

        for exc in exceptions:
            with pytest.raises(EntityNotFoundError):
                raise exc

    def test_catch_api_errors(self):
        exceptions = [
            APITimeoutError(),
            APIRateLimitError(),
        ]

        for exc in exceptions:
            with pytest.raises(APIError):
                raise exc
