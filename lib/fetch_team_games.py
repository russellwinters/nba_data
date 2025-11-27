from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams
import argparse
import pandas as pd

from lib.helpers import handle_api_errors, log_error, log_info, log_warning


@handle_api_errors
def fetch_team_games(team_id: str, season: str, output_path=None):
    """
    Fetch a team's game log for a specific season.
    
    Args:
        team_id: The NBA team abbreviation (e.g., 'PHI', 'LAL')
        season: Season string (e.g., '2018', '2022-23')
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/team_{team_id}_games_{season}.csv'
        
    Returns:
        DataFrame containing game data, or empty DataFrame if team not found
    """
    # Treat the incoming `team_id` as the team abbreviation
    team_abbr = team_id
    team_info = teams.find_team_by_abbreviation(team_abbr)
    if team_info:
        team_id_num = team_info['id']

        # Diagnostic: show what we found for the requested team
        log_info(f"Found team info: {team_info}")

        # Fetch the team's game log
        regular_season_game_log = teamgamelog.TeamGameLog(team_id=team_id_num, season=season, season_type_all_star='Regular Season')

        # Diagnostic: show the parameters used for the request
        try:
            log_info(f"Request parameters: {regular_season_game_log.parameters}")
        except Exception:
            pass

        # Diagnostic: inspect the raw/normalized response keys if available
        try:
            if getattr(regular_season_game_log, 'nba_response', None) is not None:
                norm = regular_season_game_log.nba_response.get_normalized_dict()
                log_info(f"NBA response keys: {list(norm.keys())}")
        except Exception as e:
            log_warning(f"Could not inspect nba_response: {e}")

        # Try to build a DataFrame from the endpoint
        try:
            game_data = regular_season_game_log.get_data_frames()[0]
        except Exception as e:
            log_error(f"Error getting data frames: {e}")
            return pd.DataFrame()

        # If no rows were returned, print a clear diagnostic message
        if game_data is None or game_data.empty:
            log_warning(f"No game data found for {team_abbr} in season {season}. Empty DataFrame.")
            # Still write an empty CSV so downstream steps are reproducible
            if output_path is None:
                output_path = f'data/team_{team_abbr}_games_{season}.csv'
            try:
                game_data.to_csv(output_path, index=False)
                log_info(f"Wrote empty CSV to {output_path}")
            except Exception:
                log_error("Could not write empty CSV file")
            return game_data

        # Write the (non-empty) game data to a CSV file
        if output_path is None:
            output_path = f'data/team_{team_abbr}_games_{season}.csv'
        game_data.to_csv(output_path, index=False)
        log_info(f"Wrote {output_path} ({game_data.shape[0]} rows, {game_data.shape[1]} cols)")
        print(game_data.head())
        return game_data
    else:
        log_error("Team not found", {"team_abbr": team_abbr})
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description='Fetch a team\'s game log for a specific season')
    parser.add_argument(
        '--team-id',
        required=True,
        help='NBA team abbreviation (e.g., "PHI", "LAL")'
    )
    parser.add_argument(
        '--season',
        required=True,
        help='Season string (e.g., "2018", "2022-23")'
    )
    parser.add_argument(
        '--output',
        help='Output CSV file path (default: data/team_{team_id}_games_{season}.csv)'
    )
    args = parser.parse_args()
    fetch_team_games(team_id=args.team_id, season=args.season, output_path=args.output)


if __name__ == '__main__':
    main()
