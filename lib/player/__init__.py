"""
Player submodule - Functions for fetching player-related NBA data.

This module provides functions for fetching player information, game logs,
and statistics.
"""

from .all import all, fetch_players
from .games_by_season import games_by_season, fetch_player_games
from .career_stats import career_stats, fetch_player_stats

__all__ = [
    # New names
    'all',
    'games_by_season',
    'career_stats',
    # Backward compatibility
    'fetch_players',
    'fetch_player_games',
    'fetch_player_stats',
]
