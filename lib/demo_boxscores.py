#!/usr/bin/env python3
"""
Demo: Box Score Retrieval using nba_api

This module demonstrates various ways to retrieve box score data for NBA games
using the nba_api library. It provides alternatives to TeamGameLog and TeamGameLogs.

Usage:
    # Find games for a team on a specific date
    python -m lib.demo_boxscores --team-id LAL --date 2024-01-15

    # Get box score for a specific game ID
    python -m lib.demo_boxscores --game-id 0022400123

    # Find all games on a specific date
    python -m lib.demo_boxscores --date 2024-01-15

    # Find games for a team in a date range
    python -m lib.demo_boxscores --team-id LAL --date-from 2024-01-01 --date-to 2024-01-31

Examples:
    # Get Lakers games from January 2024
    python lib/demo_boxscores.py --team-id LAL --date-from 2024-01-01 --date-to 2024-01-31

    # Get all games on Christmas Day 2023
    python lib/demo_boxscores.py --date 2023-12-25

    # Get box score for a specific game
    python lib/demo_boxscores.py --game-id 0022301234
"""

import argparse
import time
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from nba_api.stats.endpoints import (
    boxscoreadvancedv3,
    boxscoresummaryv2,
    boxscoretraditionalv3,
    leaguegamefinder,
    scoreboardv2,
)
from nba_api.stats.static import teams


def _normalize_team_id(team_id: Any) -> Optional[int]:
    """
    Resolve a team identifier to a numeric team ID.

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


def _format_date_nba(date_str: str) -> str:
    """
    Convert date string to NBA API format (MM/DD/YYYY).

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Date in MM/DD/YYYY format
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        # Already in correct format or invalid
        return date_str


def find_games_by_team_and_date(
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

    Example:
        >>> df = find_games_by_team_and_date('LAL', '2024-01-01', '2024-01-31')
        >>> print(df[['GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'PTS']])
    """
    team_id_num = _normalize_team_id(team_id)
    if team_id_num is None:
        print(f"Could not resolve team_id: {team_id!r}")
        return pd.DataFrame()

    kwargs = {
        "player_or_team_abbreviation": "T",
        "team_id_nullable": team_id_num,
        "timeout": timeout,
    }

    if date_from:
        kwargs["date_from_nullable"] = _format_date_nba(date_from)
    if date_to:
        kwargs["date_to_nullable"] = _format_date_nba(date_to)
    if season:
        kwargs["season_nullable"] = season

    try:
        finder = leaguegamefinder.LeagueGameFinder(**kwargs)
        dfs = finder.get_data_frames()
        if dfs:
            return dfs[0]
    except Exception as e:
        print(f"Error finding games: {e}")

    return pd.DataFrame()


def find_games_by_date(
    game_date: str,
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Find all games on a specific date using ScoreboardV2.

    Args:
        game_date: Date in YYYY-MM-DD format
        timeout: Request timeout in seconds

    Returns:
        DataFrame containing game headers with GAME_ID, team info, etc.

    Example:
        >>> df = find_games_by_date('2024-01-15')
        >>> print(df[['GAME_ID', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID']])
    """
    try:
        scoreboard = scoreboardv2.ScoreboardV2(
            game_date=game_date,
            timeout=timeout,
        )
        dfs = scoreboard.get_data_frames()
        # First DataFrame is GameHeader
        if dfs:
            return dfs[0]
    except Exception as e:
        print(f"Error fetching scoreboard: {e}")

    return pd.DataFrame()


def get_box_score_traditional(
    game_id: str,
    timeout: int = 30,
) -> dict:
    """
    Get traditional box score for a specific game using BoxScoreTraditionalV3.

    Args:
        game_id: NBA game ID (e.g., '0022400123')
        timeout: Request timeout in seconds

    Returns:
        Dictionary with 'player_stats' and 'team_stats' DataFrames

    Example:
        >>> result = get_box_score_traditional('0022400123')
        >>> print(result['player_stats'].head())
        >>> print(result['team_stats'])
    """
    try:
        boxscore = boxscoretraditionalv3.BoxScoreTraditionalV3(
            game_id=game_id,
            timeout=timeout,
        )
        dfs = boxscore.get_data_frames()
        if len(dfs) >= 2:
            return {
                "player_stats": dfs[0],
                "team_stats": dfs[1],
            }
    except Exception as e:
        print(f"Error fetching box score: {e}")

    return {"player_stats": pd.DataFrame(), "team_stats": pd.DataFrame()}


def get_box_score_advanced(
    game_id: str,
    timeout: int = 30,
) -> dict:
    """
    Get advanced box score for a specific game using BoxScoreAdvancedV3.

    Args:
        game_id: NBA game ID (e.g., '0022400123')
        timeout: Request timeout in seconds

    Returns:
        Dictionary with 'player_stats' and 'team_stats' DataFrames

    Example:
        >>> result = get_box_score_advanced('0022400123')
        >>> print(result['player_stats'][['playerName', 'offensiveRating', 'defensiveRating']])
    """
    try:
        boxscore = boxscoreadvancedv3.BoxScoreAdvancedV3(
            game_id=game_id,
            timeout=timeout,
        )
        dfs = boxscore.get_data_frames()
        if len(dfs) >= 2:
            return {
                "player_stats": dfs[0],
                "team_stats": dfs[1],
            }
    except Exception as e:
        print(f"Error fetching advanced box score: {e}")

    return {"player_stats": pd.DataFrame(), "team_stats": pd.DataFrame()}


def get_game_summary(
    game_id: str,
    timeout: int = 30,
) -> dict:
    """
    Get game summary including line scores using BoxScoreSummaryV2.

    Args:
        game_id: NBA game ID (e.g., '0022400123')
        timeout: Request timeout in seconds

    Returns:
        Dictionary with 'game_summary', 'line_score', 'officials', etc.

    Example:
        >>> result = get_game_summary('0022400123')
        >>> print(result['line_score'])
    """
    try:
        summary = boxscoresummaryv2.BoxScoreSummaryV2(
            game_id=game_id,
            timeout=timeout,
        )
        dfs = summary.get_data_frames()
        # BoxScoreSummaryV2 returns multiple DataFrames
        result = {}
        data_names = [
            "game_summary",
            "other_stats",
            "officials",
            "inactive_players",
            "game_info",
            "line_score",
            "last_meeting",
            "season_series",
            "available_video",
        ]
        for i, name in enumerate(data_names):
            if i < len(dfs):
                result[name] = dfs[i]
            else:
                result[name] = pd.DataFrame()
        return result
    except Exception as e:
        print(f"Error fetching game summary: {e}")

    return {}


def get_complete_box_score(
    game_id: str,
    timeout: int = 30,
    delay: float = 0.5,
) -> dict:
    """
    Get complete box score data for a game combining multiple endpoints.

    Args:
        game_id: NBA game ID (e.g., '0022400123')
        timeout: Request timeout in seconds
        delay: Delay between API calls to avoid rate limiting

    Returns:
        Dictionary with all box score data

    Example:
        >>> result = get_complete_box_score('0022400123')
        >>> print(result['traditional']['team_stats'])
        >>> print(result['summary']['line_score'])
    """
    result = {}

    # Get traditional box score
    result["traditional"] = get_box_score_traditional(game_id, timeout)
    time.sleep(delay)

    # Get advanced box score
    result["advanced"] = get_box_score_advanced(game_id, timeout)
    time.sleep(delay)

    # Get game summary
    result["summary"] = get_game_summary(game_id, timeout)

    return result


def demo_find_games_by_team(team_id: str, date_from: str, date_to: str):
    """Demo: Find games for a team in a date range."""
    print(f"\n{'='*60}")
    print(f"Finding games for {team_id} from {date_from} to {date_to}")
    print("=" * 60)

    df = find_games_by_team_and_date(team_id, date_from, date_to)

    if df.empty:
        print("No games found.")
        return []

    print(f"\nFound {len(df)} games:")
    display_cols = ["GAME_ID", "GAME_DATE", "MATCHUP", "WL", "PTS"]
    available_cols = [c for c in display_cols if c in df.columns]
    print(df[available_cols].to_string(index=False))

    return df["GAME_ID"].tolist()


def demo_find_games_by_date(game_date: str):
    """Demo: Find all games on a specific date."""
    print(f"\n{'='*60}")
    print(f"Finding all games on {game_date}")
    print("=" * 60)

    df = find_games_by_date(game_date)

    if df.empty:
        print("No games found.")
        return []

    print(f"\nFound {len(df)} games:")
    display_cols = ["GAME_ID", "HOME_TEAM_ID", "VISITOR_TEAM_ID", "GAME_STATUS_TEXT"]
    available_cols = [c for c in display_cols if c in df.columns]
    print(df[available_cols].to_string(index=False))

    return df["GAME_ID"].tolist()


def demo_get_box_score(game_id: str):
    """Demo: Get complete box score for a game."""
    print(f"\n{'='*60}")
    print(f"Getting box score for game {game_id}")
    print("=" * 60)

    # Traditional box score
    print("\n--- Traditional Box Score ---")
    trad = get_box_score_traditional(game_id)

    if not trad["team_stats"].empty:
        print("\nTeam Stats:")
        display_cols = [
            "teamName",
            "teamCity",
            "points",
            "reboundsTotal",
            "assists",
            "fieldGoalsPercentage",
        ]
        available_cols = [c for c in display_cols if c in trad["team_stats"].columns]
        if available_cols:
            print(trad["team_stats"][available_cols].to_string(index=False))
        else:
            print(trad["team_stats"].head())

    if not trad["player_stats"].empty:
        print("\nPlayer Stats (top scorers):")
        player_df = trad["player_stats"]
        if "points" in player_df.columns:
            player_df = player_df.sort_values("points", ascending=False)
        display_cols = [
            "playerName",
            "teamTricode",
            "points",
            "reboundsTotal",
            "assists",
            "minutes",
        ]
        available_cols = [c for c in display_cols if c in player_df.columns]
        if available_cols:
            print(player_df[available_cols].head(10).to_string(index=False))
        else:
            print(player_df.head(10))

    time.sleep(0.5)

    # Game summary
    print("\n--- Game Summary ---")
    summary = get_game_summary(game_id)

    if summary.get("line_score") is not None and not summary["line_score"].empty:
        print("\nLine Score:")
        line_df = summary["line_score"]
        display_cols = [
            "TEAM_ABBREVIATION",
            "PTS_QTR1",
            "PTS_QTR2",
            "PTS_QTR3",
            "PTS_QTR4",
            "PTS",
        ]
        available_cols = [c for c in display_cols if c in line_df.columns]
        if available_cols:
            print(line_df[available_cols].to_string(index=False))
        else:
            print(line_df.head())


def main():
    """Main entry point for the demo CLI."""
    parser = argparse.ArgumentParser(
        description="Demo: Box Score Retrieval using nba_api",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Find games for a team on a specific date
    python lib/demo_boxscores.py --team-id LAL --date 2024-01-15

    # Get box score for a specific game ID
    python lib/demo_boxscores.py --game-id 0022400123

    # Find all games on a specific date
    python lib/demo_boxscores.py --date 2024-01-15

    # Find games for a team in a date range
    python lib/demo_boxscores.py --team-id LAL --date-from 2024-01-01 --date-to 2024-01-31
        """,
    )

    parser.add_argument(
        "--team-id",
        dest="team_id",
        help="Team ID or abbreviation (e.g., 'LAL', '1610612747')",
    )
    parser.add_argument(
        "--date",
        help="Specific date (YYYY-MM-DD format). Used alone finds all games on that date.",
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
        "--game-id",
        dest="game_id",
        help="Specific game ID to get box score for (e.g., '0022400123')",
    )
    parser.add_argument(
        "--season",
        help="Season filter (e.g., '2023-24')",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.team_id, args.date, args.game_id]):
        parser.print_help()
        print("\nError: Must provide at least one of: --team-id, --date, or --game-id")
        return

    game_ids = []

    # If game ID provided, get box score directly
    if args.game_id:
        demo_get_box_score(args.game_id)
        return

    # Find games by team and date range
    if args.team_id and (args.date_from or args.date_to or args.date):
        date_from = args.date_from or args.date
        date_to = args.date_to or args.date
        game_ids = demo_find_games_by_team(args.team_id, date_from, date_to)

    # Find games by team only (with optional season)
    elif args.team_id:
        print(f"\n{'='*60}")
        print(f"Finding recent games for {args.team_id}")
        print("=" * 60)
        df = find_games_by_team_and_date(args.team_id, season=args.season)
        if not df.empty:
            print(f"\nFound {len(df)} games:")
            display_cols = ["GAME_ID", "GAME_DATE", "MATCHUP", "WL", "PTS"]
            available_cols = [c for c in display_cols if c in df.columns]
            print(df[available_cols].head(10).to_string(index=False))
            game_ids = df["GAME_ID"].head(5).tolist()
        else:
            print("No games found.")

    # Find games by date only
    elif args.date:
        game_ids = demo_find_games_by_date(args.date)

    # If we found games, offer to show box score for the first one
    if game_ids:
        print(f"\nTo get box score for a game, run:")
        print(f"  python lib/demo_boxscores.py --game-id {game_ids[0]}")


if __name__ == "__main__":
    main()
