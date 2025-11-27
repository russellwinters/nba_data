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
    team-games        Fetch a team's game log for a specific season
    team-game-logs    Fetch a team's filtered game logs (TeamGameLogs)
    player-stats      Fetch a player's career statistics
    player-boxscores  Fetch player box scores for a specific game
    read-stats        Read and display a CSV file containing NBA statistics

Examples:
    python fetch.py players --output data/players.csv
    python fetch.py player-games --player-id 2544 --season 2022-23
    python fetch.py team-games --team-id LAL --season 2022-23
    python fetch.py team-game-logs --team-id LAL --season 2022-23 --season-type "Regular Season" --output data/lakers_2023.csv
    python fetch.py player-boxscores --game-id 0022400123 --output data/player_boxscores.csv
    python fetch.py read-stats players.csv
"""

import argparse
import sys

from lib.fetch_players import fetch_players
from lib.fetch_teams import fetch_teams
from lib.fetch_player_games import fetch_player_games
from lib.fetch_team_games import fetch_team_games
from lib.fetch_team_game_logs import fetch_team_game_logs
from lib.fetch_player_stats import fetch_player_stats
from lib.fetch_player_boxscores_by_game import fetch_player_boxscores_by_game
from lib.read_stats import read_stats


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
    
    # team-games subcommand
    parser_team_games = subparsers.add_parser(
        'team-games',
        help='Fetch a team\'s game log for a specific season'
    )
    parser_team_games.add_argument(
        '--team-id',
        required=True,
        help='NBA team abbreviation (e.g., "PHI", "LAL")'
    )
    parser_team_games.add_argument(
        '--season',
        required=True,
        help='Season string (e.g., "2018", "2022-23")'
    )
    parser_team_games.add_argument(
        '--output',
        help='Output CSV file path (default: data/team_{team_id}_games_{season}.csv)'
    )

    # team-game-logs subcommand (uses TeamGameLogs — more flexible filters)
    parser_team_game_logs = subparsers.add_parser(
        'team-game-logs',
        help='Fetch a team\'s filtered game logs (TeamGameLogs) and save to CSV'
    )
    parser_team_game_logs.add_argument(
        '--team-id',
        dest='team_id',
        required=True,
        help='Team identifier: numeric id, abbreviation (e.g. "LAL"), or full team name',
    )
    parser_team_game_logs.add_argument(
        '--season',
        help='Season string (e.g., "2022-23"). Optional; forwarded to the endpoint as season_nullable',
    )
    parser_team_game_logs.add_argument(
        '--season-type',
        dest='season_type',
        help='Optional season type forwarded to the endpoint (e.g. "Regular Season")',
    )
    parser_team_game_logs.add_argument(
        '--output',
        help='Output CSV file path (optional). If provided, saves DataFrame to this path',
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
        
        elif args.command == 'team-games':
            fetch_team_games(
                team_id=args.team_id,
                season=args.season,
                output_path=args.output
            )

        elif args.command == 'team-game-logs':
            # fetch_team_game_logs returns a pandas DataFrame; write it if requested
            try:
                df = fetch_team_game_logs(
                    team_id=args.team_id,
                    season=args.season,
                    season_type=args.season_type,
                )
            except TypeError:
                # Backwards-compatible: if the wrapper signature differs, call with positional args
                df = fetch_team_game_logs(args.team_id, args.season)

            if df is None or (hasattr(df, 'empty') and df.empty):
                print(f"No game-log data returned for {args.team_id} (season={args.season})")
            else:
                if getattr(args, 'output', None):
                    try:
                        df.to_csv(args.output, index=False)
                        print(f"Wrote {args.output} ({getattr(df, 'shape', ('?', '?'))[0]} rows)")
                    except Exception as e:
                        print(f"Failed to write CSV to {args.output}: {e}")
                else:
                    # Show a short preview when no output file requested
                    try:
                        print(df.head())
                    except Exception:
                        print(df)
        
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
