"""Tests for lib/helpers/validation.py module."""

import pytest

from lib.helpers.exceptions import ValidationError
from lib.helpers.validation import (
    validate_date,
    validate_game_id,
    validate_player_id,
    validate_season,
    validate_team_id,
)


class TestValidatePlayerId:
    """Tests for the validate_player_id function."""

    def test_validate_player_id_valid_integer(self):
        """Test that valid integer player IDs are returned."""
        assert validate_player_id(2544) == 2544

    def test_validate_player_id_valid_string(self):
        """Test that valid string player IDs are converted to int."""
        assert validate_player_id("2544") == 2544

    def test_validate_player_id_with_whitespace(self):
        """Test that whitespace is stripped from string input."""
        assert validate_player_id("  2544  ") == 2544

    def test_validate_player_id_none_raises(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_player_id(None)
        assert "player_id" in str(exc_info.value)

    def test_validate_player_id_zero_raises(self):
        """Test that zero raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_player_id(0)

    def test_validate_player_id_negative_raises(self):
        """Test that negative numbers raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_player_id(-1)

    def test_validate_player_id_non_numeric_string_raises(self):
        """Test that non-numeric strings raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_player_id("abc")

    def test_validate_player_id_float_raises(self):
        """Test that floats raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_player_id(2544.5)

    def test_validate_player_id_bool_raises(self):
        """Test that booleans raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_player_id(True)


class TestValidateTeamId:
    """Tests for the validate_team_id function."""

    def test_validate_team_id_valid_integer(self):
        """Test that valid integer team IDs are returned."""
        assert validate_team_id(1610612747) == 1610612747

    def test_validate_team_id_numeric_string(self):
        """Test that numeric strings are converted to int."""
        assert validate_team_id("1610612747") == 1610612747

    def test_validate_team_id_abbreviation(self):
        """Test that abbreviations are returned as strings."""
        assert validate_team_id("LAL") == "LAL"

    def test_validate_team_id_full_name(self):
        """Test that full names are returned as strings."""
        result = validate_team_id("Los Angeles Lakers")
        assert result == "Los Angeles Lakers"

    def test_validate_team_id_with_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_team_id("  LAL  ") == "LAL"

    def test_validate_team_id_none_raises(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_team_id(None)
        assert "team_id" in str(exc_info.value)

    def test_validate_team_id_empty_string_raises(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_team_id("")

    def test_validate_team_id_zero_raises(self):
        """Test that zero raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_team_id(0)

    def test_validate_team_id_negative_raises(self):
        """Test that negative numbers raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_team_id(-1)

    def test_validate_team_id_bool_raises(self):
        """Test that booleans raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_team_id(True)


class TestValidateSeason:
    """Tests for the validate_season function."""

    def test_validate_season_full_format(self):
        """Test YYYY-YY format is accepted."""
        assert validate_season("2022-23") == "2022-23"

    def test_validate_season_year_only(self):
        """Test YYYY format is accepted."""
        assert validate_season("2022") == "2022"

    def test_validate_season_with_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_season("  2022-23  ") == "2022-23"

    def test_validate_season_none_raises(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_season(None)
        assert "season" in str(exc_info.value)

    def test_validate_season_empty_string_raises(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_season("")

    def test_validate_season_invalid_format_raises(self):
        """Test that invalid formats raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_season("22-23")

    def test_validate_season_non_consecutive_years_raises(self):
        """Test that non-consecutive years raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_season("2022-25")

    def test_validate_season_year_before_nba_raises(self):
        """Test that years before NBA founding raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_season("1900")

    def test_validate_season_year_too_far_future_raises(self):
        """Test that years too far in future raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_season("2200")

    @pytest.mark.parametrize("season", [
        "2022-23",
        "2023-24",
        "1999-00",  # Century boundary
        "2000-01",
    ])
    def test_validate_season_valid_formats(self, season):
        """Test various valid season formats."""
        assert validate_season(season) == season


class TestValidateDate:
    """Tests for the validate_date function."""

    def test_validate_date_valid_format(self):
        """Test valid YYYY-MM-DD format."""
        assert validate_date("2024-01-15") == "2024-01-15"

    def test_validate_date_with_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_date("  2024-01-15  ") == "2024-01-15"

    def test_validate_date_none_raises_by_default(self):
        """Test that None raises ValidationError by default."""
        with pytest.raises(ValidationError):
            validate_date(None)

    def test_validate_date_none_allowed(self):
        """Test that None is allowed when allow_none=True."""
        assert validate_date(None, allow_none=True) is None

    def test_validate_date_empty_string_raises(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("")

    def test_validate_date_empty_string_allowed_with_allow_none(self):
        """Test that empty string returns None when allow_none=True."""
        assert validate_date("", allow_none=True) is None

    def test_validate_date_invalid_format_raises(self):
        """Test that invalid formats raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("01-15-2024")

    def test_validate_date_invalid_date_raises(self):
        """Test that invalid dates raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("2024-13-01")  # Invalid month

    def test_validate_date_invalid_day_raises(self):
        """Test that invalid days raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("2024-01-32")  # Invalid day

    def test_validate_date_custom_parameter_name(self):
        """Test custom parameter name in error message."""
        with pytest.raises(ValidationError) as exc_info:
            validate_date(None, parameter_name="start_date")
        assert "start_date" in str(exc_info.value)

    @pytest.mark.parametrize("date_str", [
        "2024-01-01",
        "2024-02-29",  # Leap year
        "2024-12-31",
        "1999-06-15",
    ])
    def test_validate_date_valid_dates(self, date_str):
        """Test various valid dates."""
        assert validate_date(date_str) == date_str


class TestValidateGameId:
    """Tests for the validate_game_id function."""

    def test_validate_game_id_valid_string(self):
        """Test valid 10-digit game ID string."""
        assert validate_game_id("0022400123") == "0022400123"

    def test_validate_game_id_valid_integer(self):
        """Test valid integer game ID is converted with leading zeros."""
        assert validate_game_id(22400123) == "0022400123"

    def test_validate_game_id_with_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_game_id("  0022400123  ") == "0022400123"

    def test_validate_game_id_none_raises(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_game_id(None)
        assert "game_id" in str(exc_info.value)

    def test_validate_game_id_empty_string_raises(self):
        """Test that empty string raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_game_id("")

    def test_validate_game_id_non_numeric_raises(self):
        """Test that non-numeric strings raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_game_id("abc1234567")

    def test_validate_game_id_wrong_length_raises(self):
        """Test that wrong length raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_game_id("123456789")  # 9 digits

    def test_validate_game_id_too_long_raises(self):
        """Test that too long game ID raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_game_id("12345678901")  # 11 digits

    def test_validate_game_id_zero_raises(self):
        """Test that zero raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_game_id(0)

    def test_validate_game_id_negative_raises(self):
        """Test that negative numbers raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_game_id(-1)

    @pytest.mark.parametrize("game_id,expected", [
        ("0022400123", "0022400123"),  # Regular season
        ("0042300101", "0042300101"),  # Playoffs
        ("0012400001", "0012400001"),  # Preseason
        ("0032400001", "0032400001"),  # All-Star
    ])
    def test_validate_game_id_various_formats(self, game_id, expected):
        """Test various valid game ID formats."""
        assert validate_game_id(game_id) == expected
