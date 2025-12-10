"""
Team submodule - Functions for fetching team-related NBA data.

This module provides functions for fetching team information and game logs.
"""

from .all import all, fetch_teams
from .games import games, fetch_team_games

__all__ = [
    # New names
    'all',
    'games',
    # Backward compatibility
    'fetch_teams',
    'fetch_team_games',
]
