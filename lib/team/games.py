#!/usr/bin/env python3
"""Fetch team game box scores using `nba_api.stats.endpoints.leaguegamefinder.LeagueGameFinder`.

This module provides a wrapper around the NBA API endpoint to find games for a
team within a date range and returns a `pandas.DataFrame` for downstream processing.

Example:
    from lib.fetch_team_box_scores import fetch_team_games

    df = fetch_team_games('LAL', date_from='2024-07-01', date_to='2025-07-01')

CLI Usage:
    python lib/fetch_team_box_scores.py --team-id LAL --date-from 2024-07-01 --date-to 2025-07-01
    python lib/fetch_team_box_scores.py --team-id LAL --date 2024-01-15
    python lib/fetch_team_box_scores.py --team-id LAL --season 2023-24
"""
import argparse
from typing import Any, Optional

import pandas as pd

from nba_api.stats.endpoints import leaguegamefinder

from lib.helpers.csv_helpers import write_csv
from lib.helpers.date_helpers import format_date_nba
from lib.helpers.team_helpers import normalize_team_id
from lib.helpers.validation import validate_team_id, validate_date, validate_season
from lib.helpers.api_wrapper import api_endpoint


# Default output path for CSV files
DEFAULT_OUTPUT_PATH = "data/demo_boxscores.csv"


@api_endpoint(timeout=30)
def games(
    team_id: Any,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    season: Optional[str] = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Find games for a specific team within a date range using LeagueGameFinder.

    This is the most flexible way to find games by team and date, and is a good
    alternative to TeamGameLog and TeamGameLogs.

    Args:
        team_id: Team ID, abbreviation (e.g., 'LAL'), or full name
        date_from: Start date in YYYY-MM-DD format (optional)
        date_to: End date in YYYY-MM-DD format (optional)
        season: Season string (e.g., '2023-24') (optional)
        timeout: Request timeout in seconds

    Returns:
        DataFrame containing game data with GAME_ID, GAME_DATE, MATCHUP, etc.

    Raises:
        ValidationError: If team_id, dates, or season are invalid

    Example:
        >>> df = fetch_team_games('LAL', '2024-01-01', '2024-01-31')
        >>> print(df[['GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'PTS']])
    """
    # Validate inputs
    team_id = validate_team_id(team_id)
    date_from = validate_date(date_from, parameter_name="date_from", allow_none=True)
    date_to = validate_date(date_to, parameter_name="date_to", allow_none=True)
    if season is not None:
        season = validate_season(season)
    
    team_id_num = normalize_team_id(team_id)
    if team_id_num is None:
        print(f"Could not resolve team_id: {team_id!r}")
        return pd.DataFrame()

    kwargs = {
        "player_or_team_abbreviation": "T",
        "team_id_nullable": team_id_num,
        "timeout": timeout,
    }

    if date_from:
        kwargs["date_from_nullable"] = format_date_nba(date_from)
    if date_to:
        kwargs["date_to_nullable"] = format_date_nba(date_to)
    if season:
        kwargs["season_nullable"] = season

    finder = leaguegamefinder.LeagueGameFinder(**kwargs)
    dfs = finder.get_data_frames()
    if dfs:
        return dfs[0]

    return pd.DataFrame()


# Backward compatibility alias
fetch_team_games = games


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch team game box scores using LeagueGameFinder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Find games for a team in a date range
    python lib/fetch_team_box_scores.py --team-id LAL --date-from 2024-01-01 --date-to 2024-01-31

    # Find games for a team on a specific date
    python lib/fetch_team_box_scores.py --team-id LAL --date 2024-01-15

    # Find games for a team in a season
    python lib/fetch_team_box_scores.py --team-id LAL --season 2023-24

    # Specify custom output file
    python lib/fetch_team_box_scores.py --team-id LAL --date 2024-01-15 --output my_output.csv
        """,
    )

    parser.add_argument(
        "--team-id",
        dest="team_id",
        required=True,
        help="Team ID or abbreviation (e.g., 'LAL', '1610612747')",
    )
    parser.add_argument(
        "--date",
        help="Specific date (YYYY-MM-DD format). Sets both date-from and date-to.",
    )
    parser.add_argument(
        "--date-from",
        dest="date_from",
        help="Start date for date range (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--date-to",
        dest="date_to",
        help="End date for date range (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--season",
        help="Season filter (e.g., '2023-24')",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output CSV file path (default: {DEFAULT_OUTPUT_PATH})",
    )

    args = parser.parse_args()

    # If --date is provided, use it for both date_from and date_to
    date_from = args.date_from or args.date
    date_to = args.date_to or args.date

    # Fetch game data
    df = games(
        team_id=args.team_id,
        date_from=date_from,
        date_to=date_to,
        season=args.season,
    )

    if df.empty:
        print(f"No games found for {args.team_id}")
    else:
        print(f"\nFound {len(df)} games:")
        display_cols = ["GAME_ID", "GAME_DATE", "MATCHUP", "WL", "PTS"]
        available_cols = [c for c in display_cols if c in df.columns]
        print(df[available_cols].to_string(index=False))

        # Write to CSV
        write_csv(df, args.output)


if __name__ == "__main__":
    main()
