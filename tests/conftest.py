"""Pytest fixtures and mock data for nba_data tests.

This module provides shared fixtures for testing the nba_data project,
including mock data for NBA API responses to avoid making actual API calls.
"""

import pandas as pd
import pytest


# =============================================================================
# Mock Team Data
# =============================================================================

@pytest.fixture
def mock_teams_list():
    """Mock list of NBA teams as returned by nba_api.stats.static.teams.get_teams().
    
    This fixture provides a subset of NBA teams for testing purposes.
    Each team record includes the full set of fields returned by the API.
    
    Reference: https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
    """
    return [
        {
            "id": 1610612747,
            "full_name": "Los Angeles Lakers",
            "abbreviation": "LAL",
            "nickname": "Lakers",
            "city": "Los Angeles",
            "state": "California",
            "year_founded": 1948,
        },
        {
            "id": 1610612738,
            "full_name": "Boston Celtics",
            "abbreviation": "BOS",
            "nickname": "Celtics",
            "city": "Boston",
            "state": "Massachusetts",
            "year_founded": 1946,
        },
        {
            "id": 1610612744,
            "full_name": "Golden State Warriors",
            "abbreviation": "GSW",
            "nickname": "Warriors",
            "city": "Golden State",
            "state": "California",
            "year_founded": 1946,
        },
        {
            "id": 1610612748,
            "full_name": "Miami Heat",
            "abbreviation": "MIA",
            "nickname": "Heat",
            "city": "Miami",
            "state": "Florida",
            "year_founded": 1988,
        },
        {
            "id": 1610612751,
            "full_name": "Brooklyn Nets",
            "abbreviation": "BKN",
            "nickname": "Nets",
            "city": "Brooklyn",
            "state": "New York",
            "year_founded": 1976,
        },
    ]


@pytest.fixture
def mock_lakers_team():
    """Mock Lakers team record for testing team lookup functions."""
    return {
        "id": 1610612747,
        "full_name": "Los Angeles Lakers",
        "abbreviation": "LAL",
        "nickname": "Lakers",
        "city": "Los Angeles",
        "state": "California",
        "year_founded": 1948,
    }


# =============================================================================
# Mock Player Data
# =============================================================================

@pytest.fixture
def mock_players_list():
    """Mock list of NBA players for testing.
    
    This fixture provides a subset of NBA players with common fields
    returned by the NBA API.
    
    Reference: https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/players.md
    """
    return [
        {
            "id": 2544,
            "full_name": "LeBron James",
            "first_name": "LeBron",
            "last_name": "James",
            "is_active": True,
        },
        {
            "id": 201566,
            "full_name": "Russell Westbrook",
            "first_name": "Russell",
            "last_name": "Westbrook",
            "is_active": True,
        },
        {
            "id": 203507,
            "full_name": "Giannis Antetokounmpo",
            "first_name": "Giannis",
            "last_name": "Antetokounmpo",
            "is_active": True,
        },
        {
            "id": 201935,
            "full_name": "James Harden",
            "first_name": "James",
            "last_name": "Harden",
            "is_active": True,
        },
        {
            "id": 203999,
            "full_name": "Nikola Jokic",
            "first_name": "Nikola",
            "last_name": "Jokic",
            "is_active": True,
        },
    ]


@pytest.fixture
def mock_lebron_player():
    """Mock LeBron James player record for testing player lookup functions."""
    return {
        "id": 2544,
        "full_name": "LeBron James",
        "first_name": "LeBron",
        "last_name": "James",
        "is_active": True,
    }


# =============================================================================
# Mock Game Data
# =============================================================================

@pytest.fixture
def mock_game_finder_response():
    """Mock response from LeagueGameFinder API endpoint.
    
    This fixture provides sample game data as returned by the LeagueGameFinder
    endpoint, which is used for fetching team game box scores.
    
    Reference: https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguegamefinder.md
    """
    return pd.DataFrame({
        "SEASON_ID": ["22024", "22024", "22024"],
        "TEAM_ID": [1610612747, 1610612747, 1610612747],
        "TEAM_ABBREVIATION": ["LAL", "LAL", "LAL"],
        "TEAM_NAME": ["Los Angeles Lakers", "Los Angeles Lakers", "Los Angeles Lakers"],
        "GAME_ID": ["0022400123", "0022400145", "0022400167"],
        "GAME_DATE": ["2024-01-15", "2024-01-18", "2024-01-20"],
        "MATCHUP": ["LAL vs. BOS", "LAL @ MIA", "LAL vs. GSW"],
        "WL": ["W", "L", "W"],
        "MIN": [240, 240, 265],
        "PTS": [112, 105, 118],
        "FGM": [42, 38, 45],
        "FGA": [88, 92, 85],
        "FG_PCT": [0.477, 0.413, 0.529],
        "FG3M": [12, 10, 15],
        "FG3A": [32, 35, 30],
        "FG3_PCT": [0.375, 0.286, 0.500],
        "FTM": [16, 19, 13],
        "FTA": [22, 24, 18],
        "FT_PCT": [0.727, 0.792, 0.722],
        "OREB": [10, 8, 12],
        "DREB": [32, 30, 35],
        "REB": [42, 38, 47],
        "AST": [25, 22, 28],
        "STL": [8, 6, 10],
        "BLK": [5, 4, 7],
        "TOV": [12, 15, 10],
        "PF": [18, 20, 16],
        "PLUS_MINUS": [7, -3, 12],
    })


@pytest.fixture
def mock_player_game_log_response():
    """Mock response from PlayerGameLog API endpoint.
    
    This fixture provides sample game log data for a player.
    """
    return pd.DataFrame({
        "SEASON_ID": ["22024", "22024", "22024"],
        "Player_ID": [2544, 2544, 2544],
        "Game_ID": ["0022400123", "0022400145", "0022400167"],
        "GAME_DATE": ["JAN 15, 2024", "JAN 18, 2024", "JAN 20, 2024"],
        "MATCHUP": ["LAL vs. BOS", "LAL @ MIA", "LAL vs. GSW"],
        "WL": ["W", "L", "W"],
        "MIN": [36, 34, 38],
        "FGM": [10, 8, 12],
        "FGA": [20, 18, 22],
        "FG_PCT": [0.500, 0.444, 0.545],
        "FG3M": [2, 1, 3],
        "FG3A": [5, 4, 6],
        "FG3_PCT": [0.400, 0.250, 0.500],
        "FTM": [6, 5, 4],
        "FTA": [8, 6, 5],
        "FT_PCT": [0.750, 0.833, 0.800],
        "OREB": [1, 2, 0],
        "DREB": [8, 7, 9],
        "REB": [9, 9, 9],
        "AST": [8, 7, 10],
        "STL": [2, 1, 2],
        "BLK": [1, 0, 2],
        "TOV": [3, 4, 2],
        "PF": [2, 3, 1],
        "PTS": [28, 22, 31],
        "PLUS_MINUS": [8, -5, 15],
        "VIDEO_AVAILABLE": [1, 1, 1],
    })


@pytest.fixture
def mock_player_boxscore_response():
    """Mock response from BoxScoreTraditionalV2 API endpoint.
    
    This fixture provides sample box score data for players in a game.
    """
    return pd.DataFrame({
        "GAME_ID": ["0022400123", "0022400123", "0022400123"],
        "TEAM_ID": [1610612747, 1610612747, 1610612747],
        "TEAM_ABBREVIATION": ["LAL", "LAL", "LAL"],
        "TEAM_CITY": ["Los Angeles", "Los Angeles", "Los Angeles"],
        "PLAYER_ID": [2544, 201566, 203076],
        "PLAYER_NAME": ["LeBron James", "Russell Westbrook", "Anthony Davis"],
        "NICKNAME": ["", "", ""],
        "START_POSITION": ["F", "G", "C"],
        "COMMENT": ["", "", ""],
        "MIN": ["36:00", "32:00", "34:00"],
        "FGM": [10, 8, 9],
        "FGA": [20, 16, 18],
        "FG_PCT": [0.500, 0.500, 0.500],
        "FG3M": [2, 1, 0],
        "FG3A": [5, 3, 1],
        "FG3_PCT": [0.400, 0.333, 0.000],
        "FTM": [6, 4, 8],
        "FTA": [8, 5, 10],
        "FT_PCT": [0.750, 0.800, 0.800],
        "OREB": [1, 2, 3],
        "DREB": [8, 5, 10],
        "REB": [9, 7, 13],
        "AST": [8, 6, 3],
        "STL": [2, 1, 1],
        "BLK": [1, 0, 3],
        "TO": [3, 2, 1],
        "PF": [2, 4, 3],
        "PTS": [28, 21, 26],
        "PLUS_MINUS": [8, 5, 10],
    })


# =============================================================================
# Mock Empty Responses
# =============================================================================

@pytest.fixture
def mock_empty_dataframe():
    """Mock empty DataFrame for testing empty response handling."""
    return pd.DataFrame()


@pytest.fixture
def mock_empty_game_response():
    """Mock empty game finder response."""
    return pd.DataFrame(columns=[
        "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME",
        "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN", "PTS",
    ])


# =============================================================================
# Sample DataFrames for CSV Testing
# =============================================================================

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing CSV write operations."""
    return pd.DataFrame({
        "col1": [1, 2, 3],
        "col2": ["a", "b", "c"],
        "col3": [1.1, 2.2, 3.3],
    })


@pytest.fixture
def sample_dataframe_with_special_chars():
    """Sample DataFrame with special characters for CSV testing."""
    return pd.DataFrame({
        "name": ["O'Brien", "Smith, Jr.", "Davis \"The Beast\""],
        "value": [100, 200, 300],
    })
