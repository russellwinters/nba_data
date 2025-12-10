#!/usr/bin/env python3
"""
NBA Data Fetch CLI

A unified command-line interface for fetching and reading NBA data.

Usage:
    python fetch.py <subcommand> [options]

Available subcommands:
    players           Fetch all NBA players
    teams             Fetch all NBA teams
    player-games      Fetch a player's game log for a specific season
    team-game-boxscores  Fetch team games within a date range (LeagueGameFinder)
    player-stats      Fetch a player's career statistics
    player-boxscores  Fetch player box scores for a specific game
    read-stats        Read and display a CSV file containing NBA statistics

Examples:
    python fetch.py players --output data/players.csv
    python fetch.py player-games --player-id 2544 --season 2022-23
    python fetch.py team-game-boxscores --team-id LAL --date-from 2024-01-01 --date-to 2024-01-31
    python fetch.py player-boxscores --game-id 0022400123 --output data/player_boxscores.csv
    python fetch.py read-stats players.csv
"""

import argparse
import sys

from lib.fetch_players import fetch_players
from lib.fetch_teams import fetch_teams
from lib.fetch_player_games import fetch_player_games
from lib.fetch_player_stats import fetch_player_stats
from lib.fetch_player_boxscores_by_game import fetch_player_boxscores_by_game
from lib.read_stats import read_stats
from lib import fetch_team_box_scores


def create_parser():
    """Create and configure the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='NBA Data Fetch CLI - Unified interface for fetching and reading NBA data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True
    
    # players subcommand
    parser_players = subparsers.add_parser(
        'players',
        help='Fetch all NBA players and save to CSV'
    )
    parser_players.add_argument(
        '--output',
        default='data/players.csv',
        help='Output CSV file path (default: data/players.csv)'
    )
    
    # teams subcommand
    parser_teams = subparsers.add_parser(
        'teams',
        help='Fetch all NBA teams and save to CSV'
    )
    parser_teams.add_argument(
        '--output',
        default='data/teams.csv',
        help='Output CSV file path (default: data/teams.csv)'
    )
    
    # player-games subcommand
    parser_player_games = subparsers.add_parser(
        'player-games',
        help='Fetch a player\'s game log for a specific season'
    )
    parser_player_games.add_argument(
        '--player-id',
        type=int,
        required=True,
        help='NBA player ID'
    )
    parser_player_games.add_argument(
        '--season',
        required=True,
        help='Season string (e.g., "2005", "2022-23")'
    )
    parser_player_games.add_argument(
        '--output',
        help='Output CSV file path (default: data/{player_id}_games_{season}.csv)'
    )

    # team-game-boxscores subcommand (uses LeagueGameFinder — date range based)
    parser_team_game_boxscores = subparsers.add_parser(
        'team-game-boxscores',
        help='Fetch team games within a date range (LeagueGameFinder) and save to CSV'
    )
    parser_team_game_boxscores.add_argument(
        '--team-id',
        dest='team_id',
        required=True,
        help='Team identifier: numeric id, abbreviation (e.g. "LAL"), or full team name',
    )
    parser_team_game_boxscores.add_argument(
        '--date',
        help='Specific date (YYYY-MM-DD format). Sets both date-from and date-to.',
    )
    parser_team_game_boxscores.add_argument(
        '--date-from',
        dest='date_from',
        help='Start date for date range (YYYY-MM-DD format)',
    )
    parser_team_game_boxscores.add_argument(
        '--date-to',
        dest='date_to',
        help='End date for date range (YYYY-MM-DD format)',
    )
    parser_team_game_boxscores.add_argument(
        '--season',
        help='Season filter (e.g., "2023-24")',
    )
    parser_team_game_boxscores.add_argument(
        '--output',
        default='data/demo_boxscores.csv',
        help='Output CSV file path (default: data/demo_boxscores.csv)',
    )
    
    # player-stats subcommand
    parser_player_stats = subparsers.add_parser(
        'player-stats',
        help='Fetch a player\'s career statistics'
    )
    parser_player_stats.add_argument(
        '--player-id',
        type=int,
        required=True,
        help='NBA player ID'
    )
    parser_player_stats.add_argument(
        '--output',
        help='Output CSV file path (default: data/{player_id}_career.csv)'
    )
    
    # player-boxscores subcommand
    parser_player_boxscores = subparsers.add_parser(
        'player-boxscores',
        help='Fetch player box scores for a specific game'
    )
    parser_player_boxscores.add_argument(
        '--game-id',
        dest='game_id',
        required=True,
        help='NBA game ID (e.g., "0022400123")'
    )
    parser_player_boxscores.add_argument(
        '--output',
        default='data/player_boxscores.csv',
        help='Output CSV file path (default: data/player_boxscores.csv)'
    )
    
    # read-stats subcommand
    parser_read_stats = subparsers.add_parser(
        'read-stats',
        help='Read and display a CSV file containing NBA statistics'
    )
    parser_read_stats.add_argument(
        'filename',
        help='Name of the CSV file to read'
    )
    parser_read_stats.add_argument(
        '--data-dir',
        default='data',
        help='Directory where the file is located (default: data)'
    )
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.command == 'players':
            fetch_players(output_path=args.output)
        
        elif args.command == 'teams':
            fetch_teams(output_path=args.output)
        
        elif args.command == 'player-games':
            fetch_player_games(
                player_id=args.player_id,
                season=args.season,
                output_path=args.output
            )

        elif args.command == 'team-game-boxscores':
            # If --date is provided, use it for both date_from and date_to
            date_from = getattr(args, 'date_from', None) or getattr(args, 'date', None)
            date_to = getattr(args, 'date_to', None) or getattr(args, 'date', None)

            df = fetch_team_box_scores.fetch_team_games(
                team_id=args.team_id,
                date_from=date_from,
                date_to=date_to,
                season=getattr(args, 'season', None),
            )

            if df is None or (hasattr(df, 'empty') and df.empty):
                print(f"No games found for {args.team_id}")
            else:
                print(f"\nFound {len(df)} games:")
                display_cols = ["GAME_ID", "GAME_DATE", "MATCHUP", "WL", "PTS"]
                available_cols = [c for c in display_cols if c in df.columns]
                print(df[available_cols].to_string(index=False))

                # Write to CSV
                fetch_team_box_scores.write_csv(df, args.output)
        
        elif args.command == 'player-stats':
            fetch_player_stats(
                player_id=args.player_id,
                output_path=args.output
            )
        
        elif args.command == 'player-boxscores':
            fetch_player_boxscores_by_game(
                game_id=args.game_id,
                output_path=args.output
            )
        
        elif args.command == 'read-stats':
            read_stats(
                filename=args.filename,
                data_dir=args.data_dir
            )
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
