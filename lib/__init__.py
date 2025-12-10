"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

# Import submodules
from . import player, team, game

# Legacy imports for backward compatibility (from old file locations)
try:
    from .fetch_players import fetch_players
    from .fetch_teams import fetch_teams
    from .fetch_player_games import fetch_player_games
    from .fetch_player_stats import fetch_player_stats
    from .fetch_player_boxscores_by_game import fetch_player_boxscores_by_game
    from . import fetch_team_box_scores
except ImportError:
    # Files have been removed in later phases
    fetch_players = None
    fetch_teams = None
    fetch_player_games = None
    fetch_player_stats = None
    fetch_player_boxscores_by_game = None
    fetch_team_box_scores = None

from .read_stats import read_stats

__all__ = [
    # Submodules
    'player',
    'team',
    'game',
    # Backward compatibility functions (from old file locations)
    'fetch_players',
    'fetch_teams',
    'fetch_player_games',
    'fetch_player_stats',
    'fetch_player_boxscores_by_game',
    'read_stats',
    'fetch_team_box_scores',
]
