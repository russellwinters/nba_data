"""Input validation helpers for the nba_data project.

This module provides validation functions for common parameters used across
the nba_data fetching modules. Each validator raises a ValidationError if
the input is invalid, providing clear error messages.

Validation Functions:
    validate_player_id: Validate NBA player ID (positive integer)
    validate_team_id: Validate team ID (int, string, abbreviation, or name)
    validate_season: Validate season string format
    validate_date: Validate date in YYYY-MM-DD format
    validate_game_id: Validate NBA game ID format

Usage:
    from lib.helpers.validation import validate_player_id, validate_season

    # Raises ValidationError if invalid
    validate_player_id(2544)
    validate_season("2022-23")

    # Can also return the validated/normalized value
    player_id = validate_player_id("2544")  # Returns 2544 as int
"""

import re
from datetime import datetime
from typing import Any, Optional, Union

from lib.helpers.exceptions import ValidationError


def validate_player_id(player_id: Any) -> int:
    """Validate an NBA player ID.

    Player IDs must be positive integers. String representations of positive
    integers are also accepted and will be converted to int.

    Args:
        player_id: The player ID to validate (int or string)

    Returns:
        The validated player ID as an integer

    Raises:
        ValidationError: If player_id is None, not a valid integer,
            or not a positive number

    Examples:
        >>> validate_player_id(2544)
        2544
        >>> validate_player_id("2544")
        2544
        >>> validate_player_id(-1)  # Raises ValidationError
    """
    if player_id is None:
        raise ValidationError(
            parameter_name="player_id",
            parameter_value=player_id,
            expected="a positive integer",
        )

    # Handle string input
    if isinstance(player_id, str):
        player_id = player_id.strip()
        if not player_id.isdigit():
            raise ValidationError(
                parameter_name="player_id",
                parameter_value=player_id,
                expected="a positive integer",
            )
        player_id = int(player_id)

    # Explicitly reject booleans (bool is a subclass of int in Python)
    if isinstance(player_id, bool):
        raise ValidationError(
            parameter_name="player_id",
            parameter_value=player_id,
            expected="a positive integer",
        )

    # Validate type and value
    if not isinstance(player_id, int):
        raise ValidationError(
            parameter_name="player_id",
            parameter_value=player_id,
            expected="a positive integer",
        )

    if player_id <= 0:
        raise ValidationError(
            parameter_name="player_id",
            parameter_value=player_id,
            expected="a positive integer (greater than 0)",
        )

    return player_id


def validate_team_id(team_id: Any) -> Union[int, str]:
    """Validate a team identifier.

    Team IDs can be:
    - Numeric team ID (int or numeric string)
    - Team abbreviation (e.g., "LAL", "BOS")
    - Full team name (e.g., "Los Angeles Lakers")

    This function validates that the input is a non-empty value suitable
    for team lookup. It does NOT verify that the team actually exists in
    the NBA database - that check is performed by normalize_team_id().

    Args:
        team_id: The team ID to validate

    Returns:
        The validated team ID (int if numeric, otherwise the original string)

    Raises:
        ValidationError: If team_id is None, empty, or invalid type

    Examples:
        >>> validate_team_id(1610612747)
        1610612747
        >>> validate_team_id("LAL")
        'LAL'
        >>> validate_team_id("1610612747")
        1610612747
        >>> validate_team_id("")  # Raises ValidationError
    """
    if team_id is None:
        raise ValidationError(
            parameter_name="team_id",
            parameter_value=team_id,
            expected="team ID (int), abbreviation (e.g., 'LAL'), or team name",
        )

    # Explicitly reject booleans (bool is a subclass of int in Python)
    if isinstance(team_id, bool):
        raise ValidationError(
            parameter_name="team_id",
            parameter_value=team_id,
            expected="team ID (int), abbreviation (e.g., 'LAL'), or team name",
        )

    # Handle integer input
    if isinstance(team_id, int):
        if team_id <= 0:
            raise ValidationError(
                parameter_name="team_id",
                parameter_value=team_id,
                expected="a positive team ID",
            )
        return team_id

    # Handle string input
    if isinstance(team_id, str):
        team_id = team_id.strip()
        if not team_id:
            raise ValidationError(
                parameter_name="team_id",
                parameter_value=team_id,
                expected="team ID (int), abbreviation (e.g., 'LAL'), or team name",
            )

        # If it's a numeric string, convert to int
        if team_id.isdigit():
            return int(team_id)

        # Otherwise, return the string (abbreviation or team name)
        return team_id

    # Invalid type
    raise ValidationError(
        parameter_name="team_id",
        parameter_value=team_id,
        expected="team ID (int), abbreviation (e.g., 'LAL'), or team name",
    )


def validate_season(season: Any) -> str:
    """Validate an NBA season string.

    Accepted formats:
    - "YYYY-YY" format (e.g., "2022-23", "2023-24")
    - "YYYY" format (e.g., "2022", "2023")

    For "YYYY-YY" format, validates that the second year is one greater
    than the first year's last two digits.

    Args:
        season: The season string to validate

    Returns:
        The validated season string

    Raises:
        ValidationError: If season is None, empty, or not in a valid format

    Examples:
        >>> validate_season("2022-23")
        '2022-23'
        >>> validate_season("2022")
        '2022'
        >>> validate_season("22-23")  # Raises ValidationError
        >>> validate_season("2022-25")  # Raises ValidationError (non-consecutive)
    """
    if season is None:
        raise ValidationError(
            parameter_name="season",
            parameter_value=season,
            expected="season string in 'YYYY-YY' or 'YYYY' format (e.g., '2022-23', '2022')",
        )

    if not isinstance(season, str):
        raise ValidationError(
            parameter_name="season",
            parameter_value=season,
            expected="season string in 'YYYY-YY' or 'YYYY' format",
        )

    season = season.strip()
    if not season:
        raise ValidationError(
            parameter_name="season",
            parameter_value=season,
            expected="season string in 'YYYY-YY' or 'YYYY' format",
        )

    # Pattern for "YYYY-YY" format (e.g., "2022-23")
    full_pattern = r"^(\d{4})-(\d{2})$"
    match = re.match(full_pattern, season)
    if match:
        start_year = int(match.group(1))
        end_suffix = int(match.group(2))

        # Validate year range (reasonable NBA era)
        if start_year < 1946 or start_year > 2100:
            raise ValidationError(
                parameter_name="season",
                parameter_value=season,
                expected="year between 1946 and 2100",
            )

        # Validate that end year is consecutive
        expected_suffix = (start_year + 1) % 100
        if end_suffix != expected_suffix:
            raise ValidationError(
                parameter_name="season",
                parameter_value=season,
                expected=f"consecutive years (e.g., '{start_year}-{expected_suffix:02d}')",
            )

        return season

    # Pattern for "YYYY" format (e.g., "2022")
    year_pattern = r"^\d{4}$"
    if re.match(year_pattern, season):
        year = int(season)
        if year < 1946 or year > 2100:
            raise ValidationError(
                parameter_name="season",
                parameter_value=season,
                expected="year between 1946 and 2100",
            )
        return season

    # Invalid format
    raise ValidationError(
        parameter_name="season",
        parameter_value=season,
        expected="season string in 'YYYY-YY' or 'YYYY' format (e.g., '2022-23', '2022')",
    )


def validate_date(
    date_str: Any,
    parameter_name: str = "date",
    allow_none: bool = False,
) -> Optional[str]:
    """Validate a date string in YYYY-MM-DD format.

    Args:
        date_str: The date string to validate
        parameter_name: Name of the parameter for error messages (default: "date")
        allow_none: If True, None values are allowed and returned as-is

    Returns:
        The validated date string, or None if allow_none=True and input is None

    Raises:
        ValidationError: If date is invalid format or represents an invalid date

    Examples:
        >>> validate_date("2024-01-15")
        '2024-01-15'
        >>> validate_date(None, allow_none=True)
        None
        >>> validate_date("01-15-2024")  # Raises ValidationError
        >>> validate_date("2024-13-01")  # Raises ValidationError (invalid month)
    """
    if date_str is None:
        if allow_none:
            return None
        raise ValidationError(
            parameter_name=parameter_name,
            parameter_value=date_str,
            expected="date in 'YYYY-MM-DD' format",
        )

    if not isinstance(date_str, str):
        raise ValidationError(
            parameter_name=parameter_name,
            parameter_value=date_str,
            expected="date string in 'YYYY-MM-DD' format",
        )

    date_str = date_str.strip()
    if not date_str:
        if allow_none:
            return None
        raise ValidationError(
            parameter_name=parameter_name,
            parameter_value=date_str,
            expected="date in 'YYYY-MM-DD' format",
        )

    # Validate format with regex
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        raise ValidationError(
            parameter_name=parameter_name,
            parameter_value=date_str,
            expected="date in 'YYYY-MM-DD' format",
        )

    # Validate that it's an actual valid date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            parameter_name=parameter_name,
            parameter_value=date_str,
            expected="a valid date in 'YYYY-MM-DD' format",
        )

    return date_str


def validate_game_id(game_id: Any) -> str:
    """Validate an NBA game ID.

    NBA game IDs are typically 10-digit strings that encode information about
    the game type and date. Common formats:
    - Regular season: starts with "002" (e.g., "0022400123")
    - Playoffs: starts with "004" (e.g., "0042300101")
    - Preseason: starts with "001" (e.g., "0012400001")
    - All-Star: starts with "003" (e.g., "0032400001")

    This function validates that the game ID is a non-empty string of digits
    with the expected length.

    Args:
        game_id: The game ID to validate

    Returns:
        The validated game ID as a string

    Raises:
        ValidationError: If game_id is None, empty, or invalid format

    Examples:
        >>> validate_game_id("0022400123")
        '0022400123'
        >>> validate_game_id(22400123)  # Converts to string with leading zeros
        '0022400123'
        >>> validate_game_id("abc123")  # Raises ValidationError
    """
    if game_id is None:
        raise ValidationError(
            parameter_name="game_id",
            parameter_value=game_id,
            expected="NBA game ID (10-digit string, e.g., '0022400123')",
        )

    # Handle integer input - convert to string with leading zeros
    if isinstance(game_id, int):
        if game_id <= 0:
            raise ValidationError(
                parameter_name="game_id",
                parameter_value=game_id,
                expected="a positive game ID",
            )
        # Pad with leading zeros to 10 digits
        game_id = str(game_id).zfill(10)

    if not isinstance(game_id, str):
        raise ValidationError(
            parameter_name="game_id",
            parameter_value=game_id,
            expected="NBA game ID (10-digit string, e.g., '0022400123')",
        )

    game_id = game_id.strip()
    if not game_id:
        raise ValidationError(
            parameter_name="game_id",
            parameter_value=game_id,
            expected="NBA game ID (10-digit string, e.g., '0022400123')",
        )

    # Validate that it contains only digits
    if not game_id.isdigit():
        raise ValidationError(
            parameter_name="game_id",
            parameter_value=game_id,
            expected="NBA game ID containing only digits",
        )

    # Validate length (NBA game IDs are typically 10 digits)
    if len(game_id) != 10:
        raise ValidationError(
            parameter_name="game_id",
            parameter_value=game_id,
            expected="10-digit NBA game ID (e.g., '0022400123')",
        )

    return game_id
