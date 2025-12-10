"""
Team submodule - Functions for fetching team-related NBA data.

This module provides functions for fetching team information, game logs,
and box scores.
"""

from .fetch_teams import fetch_teams
from .fetch_team_box_scores import fetch_team_games, write_csv

# Re-export the module for backward compatibility
from . import fetch_team_box_scores

__all__ = [
    'fetch_teams',
    'fetch_team_games',
    'write_csv',
    'fetch_team_box_scores',
]
