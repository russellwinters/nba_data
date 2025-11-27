"""Team-related helper utilities."""

from typing import Any, Optional

from nba_api.stats.static import teams


def normalize_team_id(team_id: Any) -> Optional[int]:
    """Resolve a team identifier to a numeric team ID.

    Accepts an int (returned as-is), a numeric string (converted to int), a
    team abbreviation (e.g. 'LAL'), or a full team name.

    Args:
        team_id: Team ID (int), abbreviation (e.g., 'LAL'), or team name

    Returns:
        Numeric team ID or None if not found
    """
    if team_id is None:
        return None

    # Already numeric
    if isinstance(team_id, int):
        return team_id

    # Numeric string
    if isinstance(team_id, str) and team_id.isdigit():
        return int(team_id)

    # Try abbreviation
    if isinstance(team_id, str):
        team_abbr = team_id.strip().upper()
        found = teams.find_team_by_abbreviation(team_abbr)
        if found:
            return found["id"]

        # Try full name
        try:
            found = teams.find_team_by_full_name(team_id.strip())
            if found:
                return found["id"]
        except Exception:
            pass

    return None
