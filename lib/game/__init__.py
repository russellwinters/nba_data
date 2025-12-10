"""
Game submodule - Functions for fetching game-related NBA data.

This module provides functions for retrieving box scores and game summaries.
"""

from .boxscore import boxscore, get_player_boxscores, fetch_player_boxscores_by_game
from .boxscores import (
    find_games_by_team_and_date,
    find_games_by_date,
    get_box_score_traditional,
    get_box_score_advanced,
    get_game_summary,
    get_complete_box_score,
)

# Re-export the module for backward compatibility
from . import boxscores

__all__ = [
    # New names
    'boxscore',
    # Helpers
    'get_player_boxscores',
    'find_games_by_team_and_date',
    'find_games_by_date',
    'get_box_score_traditional',
    'get_box_score_advanced',
    'get_game_summary',
    'get_complete_box_score',
    # Backward compatibility
    'fetch_player_boxscores_by_game',
    'boxscores',
]
