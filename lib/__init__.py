"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

# Import submodules
from . import player, team, game

# Re-export new names from submodules
from .player import all as player_all, games_by_season, career_stats
from .team import all as team_all, games as team_games
from .game import boxscore, get_player_boxscores

from .read_stats import read_stats

__all__ = [
    # Submodules
    'player',
    'team',
    'game',
    # Player functions
    'player_all',
    'games_by_season',
    'career_stats',
    # Team functions
    'team_all',
    'team_games',
    # Game functions
    'boxscore',
    'get_player_boxscores',
    # Utilities
    'read_stats',
]
