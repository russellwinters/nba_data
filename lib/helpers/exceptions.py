"""Custom exception classes for the nba_data project.

This module defines a hierarchy of exceptions for common error scenarios
encountered when fetching NBA data. These exceptions provide clear, specific
error types that can be caught and handled appropriately by calling code.

Exception Hierarchy:
    NBADataError (base)
    ├── EntityNotFoundError
    │   ├── PlayerNotFoundError
    │   ├── TeamNotFoundError
    │   └── GameNotFoundError
    ├── APIError
    │   ├── APITimeoutError
    │   └── APIRateLimitError
    └── ValidationError

Usage:
    from lib.helpers.exceptions import PlayerNotFoundError, TeamNotFoundError

    def fetch_player(player_id):
        player = players.find_player_by_id(player_id)
        if not player:
            raise PlayerNotFoundError(player_id)
        return player
"""


class NBADataError(Exception):
    """Base exception for all nba_data errors.

    All custom exceptions in this project inherit from this class,
    allowing callers to catch all nba_data-related errors with a
    single except clause if desired.

    Attributes:
        message: Human-readable error message
    """

    def __init__(self, message: str = "An error occurred in nba_data"):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(NBADataError):
    """Base exception for entity not found errors.

    Raised when a requested entity (player, team, game) cannot be found.

    Attributes:
        entity_type: Type of entity that was not found (e.g., 'player', 'team')
        entity_id: The identifier that was searched for
    """

    def __init__(self, entity_type: str, entity_id, message: str = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        if message is None:
            message = f"{entity_type.capitalize()} not found: {entity_id!r}"
        super().__init__(message)


class PlayerNotFoundError(EntityNotFoundError):
    """Raised when a player cannot be found by ID or name.

    Attributes:
        player_id: The player ID or name that was searched for
    """

    def __init__(self, player_id, message: str = None):
        self.player_id = player_id
        super().__init__("player", player_id, message)


class TeamNotFoundError(EntityNotFoundError):
    """Raised when a team cannot be found by ID, abbreviation, or name.

    Attributes:
        team_id: The team ID, abbreviation, or name that was searched for
    """

    def __init__(self, team_id, message: str = None):
        self.team_id = team_id
        super().__init__("team", team_id, message)


class GameNotFoundError(EntityNotFoundError):
    """Raised when a game cannot be found by ID.

    Attributes:
        game_id: The game ID that was searched for
    """

    def __init__(self, game_id, message: str = None):
        self.game_id = game_id
        super().__init__("game", game_id, message)


class APIError(NBADataError):
    """Base exception for NBA API errors.

    Raised when the NBA API returns an error or behaves unexpectedly.

    Attributes:
        status_code: HTTP status code if available
        endpoint: The API endpoint that was called
    """

    def __init__(
        self, message: str = "NBA API error", status_code: int = None, endpoint: str = None
    ):
        self.status_code = status_code
        self.endpoint = endpoint
        if status_code:
            message = f"{message} (status: {status_code})"
        if endpoint:
            message = f"{message} [endpoint: {endpoint}]"
        super().__init__(message)


class APITimeoutError(APIError):
    """Raised when an API request times out.

    Attributes:
        timeout_seconds: The timeout value that was exceeded
    """

    def __init__(self, timeout_seconds: int = None, endpoint: str = None):
        self.timeout_seconds = timeout_seconds
        message = "API request timed out"
        if timeout_seconds:
            message = f"{message} after {timeout_seconds}s"
        super().__init__(message, endpoint=endpoint)


class APIRateLimitError(APIError):
    """Raised when the API rate limit is exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying, if provided by API
    """

    def __init__(self, retry_after: int = None, endpoint: str = None):
        self.retry_after = retry_after
        message = "API rate limit exceeded"
        if retry_after:
            message = f"{message} (retry after {retry_after}s)"
        super().__init__(message, status_code=429, endpoint=endpoint)


class ValidationError(NBADataError):
    """Raised when input validation fails.

    Attributes:
        parameter_name: Name of the invalid parameter
        parameter_value: The invalid value
        expected: Description of what was expected
    """

    def __init__(
        self,
        parameter_name: str,
        parameter_value=None,
        expected: str = None,
        message: str = None,
    ):
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        self.expected = expected
        if message is None:
            message = f"Invalid value for {parameter_name!r}: {parameter_value!r}"
            if expected:
                message = f"{message}. Expected: {expected}"
        super().__init__(message)
