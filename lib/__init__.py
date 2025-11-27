"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

from .fetch_players import fetch_players
from .fetch_teams import fetch_teams
from .fetch_player_games import fetch_player_games
from .fetch_team_games import fetch_team_games
from .fetch_team_game_logs import fetch_team_game_logs
from .fetch_player_stats import fetch_player_stats
from .fetch_player_boxscores_by_game import fetch_player_boxscores_by_game
from .read_stats import read_stats
from . import fetch_team_box_scores

__all__ = [
    'fetch_players',
    'fetch_teams',
    'fetch_player_games',
    'fetch_team_games',
    'fetch_team_game_logs',
    'fetch_player_stats',
    'fetch_player_boxscores_by_game',
    'read_stats',
    'fetch_team_box_scores',
]
