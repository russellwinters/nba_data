"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

# Import submodules
from . import player, team, game

# Backward-compatible imports from submodules
from .player import fetch_players, fetch_player_games, fetch_player_stats
from .team import fetch_teams, fetch_team_games
from .game import fetch_player_boxscores_by_game

# Legacy imports for backward compatibility (from old file locations)
try:
    from .fetch_players import fetch_players as _legacy_fetch_players
    from .fetch_teams import fetch_teams as _legacy_fetch_teams
    from .fetch_player_games import fetch_player_games as _legacy_fetch_player_games
    from .fetch_player_stats import fetch_player_stats as _legacy_fetch_player_stats
    from .fetch_player_boxscores_by_game import fetch_player_boxscores_by_game as _legacy_fetch_player_boxscores
    from . import fetch_team_box_scores
except ImportError:
    # Files have been removed in later phases
    fetch_team_box_scores = None

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
    'fetch_player_stats',
    'fetch_player_boxscores_by_game',
    'fetch_team_games',
    'read_stats',
    'fetch_team_box_scores',
]
