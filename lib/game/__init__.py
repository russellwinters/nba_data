"""
Game submodule - Functions for fetching game-related NBA data.

This module provides functions for retrieving box scores and game summaries.
"""

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
    'find_games_by_team_and_date',
    'find_games_by_date',
    'get_box_score_traditional',
    'get_box_score_advanced',
    'get_game_summary',
    'get_complete_box_score',
    'boxscores',
]
