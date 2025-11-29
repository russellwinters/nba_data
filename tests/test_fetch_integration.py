"""Integration tests for fetching modules with mocked API responses.

This module contains integration tests for all fetching modules in the lib/
directory. All API calls are mocked to avoid making actual network requests
during testing.

Tested Modules:
    - fetch_players.py
    - fetch_teams.py
    - fetch_player_stats.py
    - fetch_player_games.py
    - fetch_player_boxscores_by_game.py
    - fetch_team_box_scores.py
"""

import pandas as pd
import pytest


# =============================================================================
# Tests for fetch_players.py
# =============================================================================


class TestFetchPlayers:
    """Integration tests for fetch_players module."""

    def test_fetch_players_returns_dataframe(self, mocker, mock_players_list, tmp_path):
        """Test that fetch_players returns a DataFrame with player data."""
        mocker.patch(
            'lib.fetch_players.players.get_players',
            return_value=mock_players_list
        )
        mocker.patch('lib.fetch_players.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_players import fetch_players

        output_path = str(tmp_path / "players.csv")
        result = fetch_players(output_path=output_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(mock_players_list)
        assert 'full_name' in result.columns
        assert 'id' in result.columns

    def test_fetch_players_empty_response(self, mocker, tmp_path):
        """Test fetch_players with empty API response."""
        mocker.patch(
            'lib.fetch_players.players.get_players',
            return_value=[]
        )
        mocker.patch('lib.fetch_players.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_players import fetch_players

        output_path = str(tmp_path / "players.csv")
        result = fetch_players(output_path=output_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_fetch_players_contains_expected_fields(self, mocker, mock_players_list, tmp_path):
        """Test that returned DataFrame contains expected player fields."""
        mocker.patch(
            'lib.fetch_players.players.get_players',
            return_value=mock_players_list
        )
        mocker.patch('lib.fetch_players.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_players import fetch_players

        output_path = str(tmp_path / "players.csv")
        result = fetch_players(output_path=output_path)

        expected_columns = ['id', 'full_name', 'first_name', 'last_name', 'is_active']
        for col in expected_columns:
            assert col in result.columns

    def test_fetch_players_writes_csv(self, mocker, mock_players_list, tmp_path):
        """Test that fetch_players calls write_csv with correct arguments."""
        mocker.patch(
            'lib.fetch_players.players.get_players',
            return_value=mock_players_list
        )
        mock_write_csv = mocker.patch('lib.fetch_players.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_players import fetch_players

        output_path = str(tmp_path / "players.csv")
        fetch_players(output_path=output_path)

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == output_path


# =============================================================================
# Tests for fetch_teams.py
# =============================================================================


class TestFetchTeams:
    """Integration tests for fetch_teams module."""

    def test_fetch_teams_returns_dataframe(self, mocker, mock_teams_list, tmp_path):
        """Test that fetch_teams returns a DataFrame with team data."""
        mocker.patch(
            'lib.fetch_teams.teams.get_teams',
            return_value=mock_teams_list
        )
        mocker.patch('lib.fetch_teams.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_teams import fetch_teams

        output_path = str(tmp_path / "teams.csv")
        result = fetch_teams(output_path=output_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(mock_teams_list)
        assert 'full_name' in result.columns
        assert 'abbreviation' in result.columns

    def test_fetch_teams_empty_response(self, mocker, tmp_path):
        """Test fetch_teams with empty API response."""
        mocker.patch(
            'lib.fetch_teams.teams.get_teams',
            return_value=[]
        )
        mocker.patch('lib.fetch_teams.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_teams import fetch_teams

        output_path = str(tmp_path / "teams.csv")
        result = fetch_teams(output_path=output_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_fetch_teams_contains_expected_fields(self, mocker, mock_teams_list, tmp_path):
        """Test that returned DataFrame contains expected team fields."""
        mocker.patch(
            'lib.fetch_teams.teams.get_teams',
            return_value=mock_teams_list
        )
        mocker.patch('lib.fetch_teams.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_teams import fetch_teams

        output_path = str(tmp_path / "teams.csv")
        result = fetch_teams(output_path=output_path)

        expected_columns = ['id', 'full_name', 'abbreviation', 'nickname', 'city', 'state']
        for col in expected_columns:
            assert col in result.columns

    def test_fetch_teams_writes_csv(self, mocker, mock_teams_list, tmp_path):
        """Test that fetch_teams calls write_csv with correct arguments."""
        mocker.patch(
            'lib.fetch_teams.teams.get_teams',
            return_value=mock_teams_list
        )
        mock_write_csv = mocker.patch('lib.fetch_teams.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_teams import fetch_teams

        output_path = str(tmp_path / "teams.csv")
        fetch_teams(output_path=output_path)

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == output_path


# =============================================================================
# Tests for fetch_player_stats.py
# =============================================================================


class TestFetchPlayerStats:
    """Integration tests for fetch_player_stats module."""

    def test_fetch_player_stats_returns_dataframe(
        self, mocker, mock_lebron_player, mock_player_career_stats, tmp_path
    ):
        """Test that fetch_player_stats returns a DataFrame with career stats."""
        mocker.patch(
            'lib.fetch_player_stats.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_stats._fetch_career_stats',
            return_value=mock_player_career_stats
        )
        mocker.patch('lib.fetch_player_stats.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_stats import fetch_player_stats

        output_path = str(tmp_path / "career.csv")
        result = fetch_player_stats(player_id=2544, output_path=output_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_fetch_player_stats_player_not_found(self, mocker, tmp_path):
        """Test fetch_player_stats when player is not found."""
        mocker.patch(
            'lib.fetch_player_stats.players.find_player_by_id',
            return_value=None
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_stats import fetch_player_stats

        output_path = str(tmp_path / "career.csv")
        result = fetch_player_stats(player_id=99999999, output_path=output_path)

        assert result is None

    def test_fetch_player_stats_empty_career_stats(
        self, mocker, mock_lebron_player, tmp_path
    ):
        """Test fetch_player_stats when career stats are empty."""
        mocker.patch(
            'lib.fetch_player_stats.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_stats._fetch_career_stats',
            return_value=pd.DataFrame()
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_stats import fetch_player_stats

        output_path = str(tmp_path / "career.csv")
        result = fetch_player_stats(player_id=2544, output_path=output_path)

        assert result is None

    def test_fetch_player_stats_writes_csv(
        self, mocker, mock_lebron_player, mock_player_career_stats, tmp_path
    ):
        """Test that fetch_player_stats calls write_csv with correct arguments."""
        mocker.patch(
            'lib.fetch_player_stats.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_stats._fetch_career_stats',
            return_value=mock_player_career_stats
        )
        mock_write_csv = mocker.patch('lib.fetch_player_stats.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_stats import fetch_player_stats

        output_path = str(tmp_path / "career.csv")
        fetch_player_stats(player_id=2544, output_path=output_path)

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == output_path

    def test_fetch_player_stats_default_output_path(
        self, mocker, mock_lebron_player, mock_player_career_stats
    ):
        """Test fetch_player_stats uses default output path when none specified."""
        mocker.patch(
            'lib.fetch_player_stats.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_stats._fetch_career_stats',
            return_value=mock_player_career_stats
        )
        mock_write_csv = mocker.patch('lib.fetch_player_stats.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_stats import fetch_player_stats

        fetch_player_stats(player_id=2544)

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == 'data/2544_career.csv'


# =============================================================================
# Tests for fetch_player_games.py
# =============================================================================


class TestFetchPlayerGames:
    """Integration tests for fetch_player_games module."""

    def test_fetch_player_games_returns_dataframe(
        self, mocker, mock_lebron_player, mock_player_game_log_response, tmp_path
    ):
        """Test that fetch_player_games returns a DataFrame with game data."""
        mocker.patch(
            'lib.fetch_player_games.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_games._fetch_player_game_log',
            return_value=mock_player_game_log_response
        )
        mocker.patch('lib.fetch_player_games.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_games import fetch_player_games

        output_path = str(tmp_path / "games.csv")
        result = fetch_player_games(player_id=2544, season="2023-24", output_path=output_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_fetch_player_games_player_not_found(self, mocker, tmp_path):
        """Test fetch_player_games when player is not found."""
        mocker.patch(
            'lib.fetch_player_games.players.find_player_by_id',
            return_value=None
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_games import fetch_player_games

        output_path = str(tmp_path / "games.csv")
        result = fetch_player_games(player_id=99999999, season="2023-24", output_path=output_path)

        assert result is None

    def test_fetch_player_games_empty_game_log(
        self, mocker, mock_lebron_player, tmp_path
    ):
        """Test fetch_player_games when game log is empty."""
        mocker.patch(
            'lib.fetch_player_games.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_games._fetch_player_game_log',
            return_value=pd.DataFrame()
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_games import fetch_player_games

        output_path = str(tmp_path / "games.csv")
        result = fetch_player_games(player_id=2544, season="2023-24", output_path=output_path)

        assert result is None

    def test_fetch_player_games_writes_csv(
        self, mocker, mock_lebron_player, mock_player_game_log_response, tmp_path
    ):
        """Test that fetch_player_games calls write_csv with correct arguments."""
        mocker.patch(
            'lib.fetch_player_games.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_games._fetch_player_game_log',
            return_value=mock_player_game_log_response
        )
        mock_write_csv = mocker.patch('lib.fetch_player_games.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_games import fetch_player_games

        output_path = str(tmp_path / "games.csv")
        fetch_player_games(player_id=2544, season="2023-24", output_path=output_path)

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == output_path

    def test_fetch_player_games_default_output_path(
        self, mocker, mock_lebron_player, mock_player_game_log_response
    ):
        """Test fetch_player_games uses default output path when none specified."""
        mocker.patch(
            'lib.fetch_player_games.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_games._fetch_player_game_log',
            return_value=mock_player_game_log_response
        )
        mock_write_csv = mocker.patch('lib.fetch_player_games.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_games import fetch_player_games

        fetch_player_games(player_id=2544, season="2023-24")

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == 'data/2544_games_2023-24.csv'

    def test_fetch_player_games_contains_expected_stats(
        self, mocker, mock_lebron_player, mock_player_game_log_response, tmp_path
    ):
        """Test that returned DataFrame contains expected game stats columns."""
        mocker.patch(
            'lib.fetch_player_games.players.find_player_by_id',
            return_value=mock_lebron_player
        )
        mocker.patch(
            'lib.fetch_player_games._fetch_player_game_log',
            return_value=mock_player_game_log_response
        )
        mocker.patch('lib.fetch_player_games.write_csv', return_value=True)
        mocker.patch('builtins.print')

        from lib.fetch_player_games import fetch_player_games

        output_path = str(tmp_path / "games.csv")
        result = fetch_player_games(player_id=2544, season="2023-24", output_path=output_path)

        expected_columns = ['Game_ID', 'MATCHUP', 'PTS', 'REB', 'AST']
        for col in expected_columns:
            assert col in result.columns


# =============================================================================
# Tests for fetch_player_boxscores_by_game.py
# =============================================================================


class TestFetchPlayerBoxscoresByGame:
    """Integration tests for fetch_player_boxscores_by_game module."""

    def test_get_player_boxscores_returns_dataframe(
        self, mocker, mock_player_boxscore_response
    ):
        """Test that get_player_boxscores returns a DataFrame with box score data."""
        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = [mock_player_boxscore_response]
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )

        from lib.fetch_player_boxscores_by_game import get_player_boxscores

        result = get_player_boxscores(game_id="0022400123")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_get_player_boxscores_empty_response(self, mocker):
        """Test get_player_boxscores with empty API response."""
        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = [pd.DataFrame()]
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )

        from lib.fetch_player_boxscores_by_game import get_player_boxscores

        result = get_player_boxscores(game_id="0022400123")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_get_player_boxscores_no_dataframes(self, mocker):
        """Test get_player_boxscores when API returns no DataFrames."""
        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = []
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )

        from lib.fetch_player_boxscores_by_game import get_player_boxscores

        result = get_player_boxscores(game_id="0022400123")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_fetch_player_boxscores_by_game_writes_csv(
        self, mocker, mock_player_boxscore_response, tmp_path
    ):
        """Test that fetch_player_boxscores_by_game calls write_csv."""
        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = [mock_player_boxscore_response]
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )
        mock_write_csv = mocker.patch(
            'lib.fetch_player_boxscores_by_game.write_csv',
            return_value=True
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_boxscores_by_game import fetch_player_boxscores_by_game

        output_path = str(tmp_path / "boxscores.csv")
        fetch_player_boxscores_by_game(game_id="0022400123", output_path=output_path)

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == output_path

    def test_fetch_player_boxscores_by_game_empty_no_write(self, mocker, tmp_path):
        """Test that no CSV is written when box score data is empty."""
        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = [pd.DataFrame()]
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )
        mock_write_csv = mocker.patch(
            'lib.fetch_player_boxscores_by_game.write_csv',
            return_value=True
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_boxscores_by_game import fetch_player_boxscores_by_game

        output_path = str(tmp_path / "boxscores.csv")
        fetch_player_boxscores_by_game(game_id="0022400123", output_path=output_path)

        mock_write_csv.assert_not_called()

    def test_fetch_player_boxscores_by_game_default_output_path(
        self, mocker, mock_player_boxscore_response
    ):
        """Test fetch_player_boxscores_by_game uses default output path."""
        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = [mock_player_boxscore_response]
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )
        mock_write_csv = mocker.patch(
            'lib.fetch_player_boxscores_by_game.write_csv',
            return_value=True
        )
        mocker.patch('builtins.print')

        from lib.fetch_player_boxscores_by_game import fetch_player_boxscores_by_game

        fetch_player_boxscores_by_game(game_id="0022400123")

        mock_write_csv.assert_called_once()
        call_args = mock_write_csv.call_args
        assert call_args[0][1] == "data/player_boxscores.csv"

    def test_get_player_boxscores_normalizes_columns(
        self, mocker
    ):
        """Test that get_player_boxscores normalizes column names."""
        # Create response with non-canonical column names
        raw_response = pd.DataFrame({
            "gameId": ["0022400123"],
            "personId": [2544],
            "firstName": ["LeBron"],
            "familyName": ["James"],
            "teamId": [1610612747],
            "teamTricode": ["LAL"],
            "minutes": ["36:00"],
            "points": [28],
            "reboundsTotal": [9],
            "assists": [8],
            "steals": [2],
            "blocks": [1],
            "turnovers": [3],
            "foulsPersonal": [2],
            "plusMinusPoints": [8],
        })

        mock_boxscore = mocker.MagicMock()
        mock_boxscore.get_data_frames.return_value = [raw_response]
        mocker.patch(
            'lib.fetch_player_boxscores_by_game.boxscoretraditionalv3.BoxScoreTraditionalV3',
            return_value=mock_boxscore
        )

        from lib.fetch_player_boxscores_by_game import get_player_boxscores

        result = get_player_boxscores(game_id="0022400123")

        # Check that columns were normalized
        assert 'GAME_ID' in result.columns
        assert 'PLAYER_ID' in result.columns
        assert 'PLAYER_NAME' in result.columns
        assert 'TEAM_ID' in result.columns
        assert 'TEAM_ABBREVIATION' in result.columns


# =============================================================================
# Tests for fetch_team_box_scores.py
# =============================================================================


class TestFetchTeamBoxScores:
    """Integration tests for fetch_team_box_scores module."""

    def test_fetch_team_games_returns_dataframe(
        self, mocker, mock_lakers_team, mock_game_finder_response
    ):
        """Test that fetch_team_games returns a DataFrame with game data."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=1610612747
        )
        mock_finder = mocker.MagicMock()
        mock_finder.get_data_frames.return_value = [mock_game_finder_response]
        mocker.patch(
            'lib.fetch_team_box_scores.leaguegamefinder.LeagueGameFinder',
            return_value=mock_finder
        )

        from lib.fetch_team_box_scores import fetch_team_games

        result = fetch_team_games(team_id="LAL", date_from="2024-01-01", date_to="2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_fetch_team_games_empty_response(self, mocker):
        """Test fetch_team_games with empty API response."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=1610612747
        )
        mock_finder = mocker.MagicMock()
        mock_finder.get_data_frames.return_value = [pd.DataFrame()]
        mocker.patch(
            'lib.fetch_team_box_scores.leaguegamefinder.LeagueGameFinder',
            return_value=mock_finder
        )

        from lib.fetch_team_box_scores import fetch_team_games

        result = fetch_team_games(team_id="LAL", date_from="2024-01-01", date_to="2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_fetch_team_games_team_not_found(self, mocker):
        """Test fetch_team_games when team is not found."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=None
        )
        mocker.patch('builtins.print')

        from lib.fetch_team_box_scores import fetch_team_games

        result = fetch_team_games(team_id="XYZ", date_from="2024-01-01", date_to="2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_fetch_team_games_no_dataframes(self, mocker):
        """Test fetch_team_games when API returns no DataFrames."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=1610612747
        )
        mock_finder = mocker.MagicMock()
        mock_finder.get_data_frames.return_value = []
        mocker.patch(
            'lib.fetch_team_box_scores.leaguegamefinder.LeagueGameFinder',
            return_value=mock_finder
        )

        from lib.fetch_team_box_scores import fetch_team_games

        result = fetch_team_games(team_id="LAL", date_from="2024-01-01", date_to="2024-01-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_fetch_team_games_with_season(
        self, mocker, mock_game_finder_response
    ):
        """Test fetch_team_games with season filter."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=1610612747
        )
        mock_finder = mocker.MagicMock()
        mock_finder.get_data_frames.return_value = [mock_game_finder_response]
        mock_game_finder = mocker.patch(
            'lib.fetch_team_box_scores.leaguegamefinder.LeagueGameFinder',
            return_value=mock_finder
        )

        from lib.fetch_team_box_scores import fetch_team_games

        result = fetch_team_games(team_id="LAL", season="2023-24")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # Verify season was passed to LeagueGameFinder
        call_kwargs = mock_game_finder.call_args.kwargs
        assert call_kwargs.get('season_nullable') == "2023-24"

    def test_fetch_team_games_contains_expected_columns(
        self, mocker, mock_game_finder_response
    ):
        """Test that returned DataFrame contains expected game columns."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=1610612747
        )
        mock_finder = mocker.MagicMock()
        mock_finder.get_data_frames.return_value = [mock_game_finder_response]
        mocker.patch(
            'lib.fetch_team_box_scores.leaguegamefinder.LeagueGameFinder',
            return_value=mock_finder
        )

        from lib.fetch_team_box_scores import fetch_team_games

        result = fetch_team_games(team_id="LAL", date_from="2024-01-01", date_to="2024-01-31")

        expected_columns = ['GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'PTS']
        for col in expected_columns:
            assert col in result.columns

    def test_fetch_team_games_date_formatting(
        self, mocker, mock_game_finder_response
    ):
        """Test that dates are properly formatted for the API."""
        mocker.patch(
            'lib.fetch_team_box_scores.normalize_team_id',
            return_value=1610612747
        )
        mock_finder = mocker.MagicMock()
        mock_finder.get_data_frames.return_value = [mock_game_finder_response]
        mock_game_finder = mocker.patch(
            'lib.fetch_team_box_scores.leaguegamefinder.LeagueGameFinder',
            return_value=mock_finder
        )

        from lib.fetch_team_box_scores import fetch_team_games

        fetch_team_games(team_id="LAL", date_from="2024-01-15", date_to="2024-01-31")

        call_kwargs = mock_game_finder.call_args.kwargs
        # Dates should be formatted to MM/DD/YYYY for the NBA API
        assert call_kwargs.get('date_from_nullable') == "01/15/2024"
        assert call_kwargs.get('date_to_nullable') == "01/31/2024"


# =============================================================================
# Validation Error Tests
# =============================================================================


class TestFetchModuleValidation:
    """Tests for input validation in fetching modules."""

    def test_fetch_player_stats_invalid_player_id(self, mocker):
        """Test fetch_player_stats raises ValidationError for invalid player_id."""
        from lib.helpers.exceptions import ValidationError
        from lib.fetch_player_stats import fetch_player_stats

        with pytest.raises(ValidationError):
            fetch_player_stats(player_id=-1)

    def test_fetch_player_games_invalid_season(self, mocker):
        """Test fetch_player_games raises ValidationError for invalid season."""
        from lib.helpers.exceptions import ValidationError
        from lib.fetch_player_games import fetch_player_games

        with pytest.raises(ValidationError):
            fetch_player_games(player_id=2544, season="invalid")

    def test_get_player_boxscores_invalid_game_id(self, mocker):
        """Test get_player_boxscores raises ValidationError for invalid game_id."""
        from lib.helpers.exceptions import ValidationError
        from lib.fetch_player_boxscores_by_game import get_player_boxscores

        with pytest.raises(ValidationError):
            get_player_boxscores(game_id="abc")

    def test_fetch_team_games_invalid_team_id(self, mocker):
        """Test fetch_team_games raises ValidationError for invalid team_id."""
        from lib.helpers.exceptions import ValidationError
        from lib.fetch_team_box_scores import fetch_team_games

        with pytest.raises(ValidationError):
            fetch_team_games(team_id=None)
