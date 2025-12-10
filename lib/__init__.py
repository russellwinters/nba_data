"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

# Import submodules
from . import player, team, game

# Backward-compatible imports - re-export from submodules
from .player import fetch_players, fetch_player_games, fetch_player_stats
from .team import fetch_teams, fetch_team_games
from .game import fetch_player_boxscores_by_game

from .read_stats import read_stats

__all__ = [
    # Submodules
    'player',
    'team',
    'game',
    # Backward compatibility functions
    'fetch_players',
    'fetch_teams',
    'fetch_player_games',
    'fetch_team_games',
    'fetch_player_stats',
    'fetch_player_boxscores_by_game',
    'read_stats',
]
