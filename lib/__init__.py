"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

# Import submodules
from . import player, team, game


from .read_stats import read_stats

__all__ = [
    # Submodules
    "player",
    "team",
    "game",
    # Utilities
    "read_stats",
]
