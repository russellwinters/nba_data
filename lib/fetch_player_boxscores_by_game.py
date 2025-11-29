#!/usr/bin/env python3
"""Fetch player box scores for a given game using nba_api.

This module provides functions to fetch individual player box scores for both
teams given a `game_id`, and write the player-level data to a CSV file.

Usage:
    # Get player box scores for a specific game
    python lib/fetch_player_boxscores_by_game.py --game-id 0022400123

    # Specify custom output file
    python lib/fetch_player_boxscores_by_game.py --game-id 0022400123 --output my_output.csv

Example:
    from lib.fetch_player_boxscores_by_game import get_player_boxscores

    df = get_player_boxscores('0022400123')
"""

import argparse
from typing import Optional

import pandas as pd

from nba_api.stats.endpoints import boxscoretraditionalv3

from lib.helpers.csv_helpers import write_csv
from lib.helpers.validation import validate_game_id
from lib.helpers.api_wrapper import api_endpoint


# Default output path for player box score CSV files
DEFAULT_PLAYER_BOX_SCORES_PATH = "data/player_boxscores.csv"

# Column mapping from API column names to canonical output columns
# The API may return different column names; this maps them to our canonical set
COLUMN_MAP = {
    # Player identification
    "gameId": "GAME_ID",
    "GAME_ID": "GAME_ID",
    "personId": "PLAYER_ID",
    "playerId": "PLAYER_ID",
    "PLAYER_ID": "PLAYER_ID",
    "firstName": "FIRST_NAME",
    "familyName": "LAST_NAME",
    "playerName": "PLAYER_NAME",
    "PLAYER_NAME": "PLAYER_NAME",
    "name": "PLAYER_NAME",
    # Team identification
    "teamId": "TEAM_ID",
    "TEAM_ID": "TEAM_ID",
    "teamTricode": "TEAM_ABBREVIATION",
    "teamAbbreviation": "TEAM_ABBREVIATION",
    "TEAM_ABBREVIATION": "TEAM_ABBREVIATION",
    # Core stats
    "minutes": "MIN",
    "MIN": "MIN",
    "points": "PTS",
    "PTS": "PTS",
    "reboundsTotal": "REB",
    "REB": "REB",
    "assists": "AST",
    "AST": "AST",
    "steals": "STL",
    "STL": "STL",
    "blocks": "BLK",
    "BLK": "BLK",
    "turnovers": "TOV",
    "TO": "TOV",
    "TOV": "TOV",
    "foulsPersonal": "PF",
    "PF": "PF",
    "plusMinusPoints": "PLUS_MINUS",
    "PLUS_MINUS": "PLUS_MINUS",
    # Shooting stats
    "fieldGoalsMade": "FGM",
    "FGM": "FGM",
    "fieldGoalsAttempted": "FGA",
    "FGA": "FGA",
    "fieldGoalsPercentage": "FG_PCT",
    "FG_PCT": "FG_PCT",
    "threePointersMade": "FG3M",
    "FG3M": "FG3M",
    "threePointersAttempted": "FG3A",
    "FG3A": "FG3A",
    "threePointersPercentage": "FG3_PCT",
    "FG3_PCT": "FG3_PCT",
    "freeThrowsMade": "FTM",
    "FTM": "FTM",
    "freeThrowsAttempted": "FTA",
    "FTA": "FTA",
    "freeThrowsPercentage": "FT_PCT",
    "FT_PCT": "FT_PCT",
}

# Canonical output columns in order
CANONICAL_COLUMNS = [
    "GAME_ID",
    "PLAYER_ID",
    "PLAYER_NAME",
    "TEAM_ID",
    "TEAM_ABBREVIATION",
    "MIN",
    "PTS",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PLUS_MINUS",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame column names to canonical output columns.

    Args:
        df: DataFrame with possibly non-canonical column names

    Returns:
        DataFrame with normalized column names
    """
    if df.empty:
        return df

    # Build rename mapping for columns that exist in the dataframe
    rename_map = {}
    for old_col in df.columns:
        if old_col in COLUMN_MAP:
            rename_map[old_col] = COLUMN_MAP[old_col]

    # Rename columns
    df = df.rename(columns=rename_map)

    # Handle playerName construction if firstName and familyName are present
    if "FIRST_NAME" in df.columns and "LAST_NAME" in df.columns:
        if "PLAYER_NAME" not in df.columns:
            df["PLAYER_NAME"] = df["FIRST_NAME"] + " " + df["LAST_NAME"]

    # Select only canonical columns that exist in the DataFrame
    available_cols = [col for col in CANONICAL_COLUMNS if col in df.columns]
    if available_cols:
        df = df[available_cols]

    return df


@api_endpoint(timeout=30)
def get_player_boxscores(
    game_id: str,
    timeout: int = 30,
) -> pd.DataFrame:
    """Fetch player box scores for a specific game.

    Retrieves traditional box score data for the provided game_id and returns
    a normalized DataFrame with player rows for both teams.

    Args:
        game_id: NBA game ID (e.g., '0022400123')
        timeout: Request timeout in seconds

    Returns:
        DataFrame containing player box scores with canonical column names,
        or an empty DataFrame if the request fails.

    Raises:
        ValidationError: If game_id is invalid

    Example:
        >>> df = get_player_boxscores('0022400123')
        >>> print(df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'REB', 'AST']])
    """
    # Validate inputs
    game_id = validate_game_id(game_id)
    
    boxscore = boxscoretraditionalv3.BoxScoreTraditionalV3(
        game_id=game_id,
        timeout=timeout,
    )
    dfs = boxscore.get_data_frames()

    # First DataFrame contains player stats
    if dfs and len(dfs) >= 1:
        player_df = dfs[0]
        if player_df is not None and not player_df.empty:
            # Add GAME_ID column if not present
            if "gameId" not in player_df.columns and "GAME_ID" not in player_df.columns:
                player_df["GAME_ID"] = game_id

            # Normalize column names
            player_df = _normalize_columns(player_df)
            return player_df

    return pd.DataFrame()


def fetch_player_boxscores_by_game(
    game_id: str,
    output_path: Optional[str] = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """Fetch player box scores for a game and write to CSV.

    Args:
        game_id: NBA game ID (e.g., '0022400123')
        output_path: Optional path to save CSV. Defaults to DEFAULT_PLAYER_BOX_SCORES_PATH.
        timeout: Request timeout in seconds

    Returns:
        DataFrame containing player box scores

    Example:
        >>> df = fetch_player_boxscores_by_game('0022400123')
        >>> # Writes to data/player_boxscores.csv by default
    """
    if output_path is None:
        output_path = DEFAULT_PLAYER_BOX_SCORES_PATH

    df = get_player_boxscores(game_id, timeout)

    if df.empty:
        print(f"No player box score data found for game {game_id}")
        return df

    write_csv(df, output_path)

    # Show preview
    try:
        print(df.head())
    except Exception:
        pass

    return df


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch player box scores for a specific NBA game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Get player box scores for a specific game
    python lib/fetch_player_boxscores_by_game.py --game-id 0022400123

    # Specify custom output file
    python lib/fetch_player_boxscores_by_game.py --game-id 0022400123 --output my_output.csv
        """,
    )

    parser.add_argument(
        "--game-id",
        dest="game_id",
        required=True,
        help="NBA game ID (e.g., '0022400123')",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_PLAYER_BOX_SCORES_PATH,
        help=f"Output CSV file path (default: {DEFAULT_PLAYER_BOX_SCORES_PATH})",
    )

    args = parser.parse_args()

    fetch_player_boxscores_by_game(
        game_id=args.game_id,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
