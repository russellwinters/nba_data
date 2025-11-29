from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import argparse

import pandas as pd

from lib.helpers.csv_helpers import write_csv
from lib.helpers.api_wrapper import api_endpoint_wrapper


@api_endpoint_wrapper(timeout=30, max_retries=3, return_empty_df_on_error=True)
def _fetch_game_log(player_id: int, season: str, timeout: int = 30) -> pd.DataFrame:
    """
    Internal function to fetch player game log from NBA API.
    
    Args:
        player_id: The NBA player ID
        season: Season string (e.g., '2005', '2022-23')
        timeout: Request timeout in seconds
        
    Returns:
        DataFrame containing game data
    """
    regular_season_game_log = playergamelog.PlayerGameLog(
        player_id=player_id, 
        season=season,
        timeout=timeout
    )
    dfs = regular_season_game_log.get_data_frames()
    if dfs:
        return dfs[0]
    return pd.DataFrame()


def fetch_player_games(player_id: int, season: str, output_path=None):
    """
    Fetch a player's game log for a specific season.
    
    Args:
        player_id: The NBA player ID
        season: Season string (e.g., '2005', '2022-23')
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/{player_id}_games_{season}.csv'
        
    Returns:
        DataFrame containing game data, or empty DataFrame if player not found
    """
    player = players.find_player_by_id(player_id)
    if player:
        resolved_player_id = player['id']

        # Fetch the player's game log using decorated function
        game_data = _fetch_game_log(resolved_player_id, season)
        
        if game_data.empty:
            print(f"No game data found for player {player_id}")
            return game_data
        
        # Write the game data to a CSV file
        if output_path is None:
            output_path = f'data/{resolved_player_id}_games_{season}.csv'
        write_csv(game_data, output_path)
        print(game_data)
        return game_data
    else:
        print("Player not found")
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description='Fetch a player\'s game log for a specific season')
    parser.add_argument(
        '--player-id',
        type=int,
        required=True,
        help='NBA player ID'
    )
    parser.add_argument(
        '--season',
        required=True,
        help='Season string (e.g., "2005", "2022-23")'
    )
    parser.add_argument(
        '--output',
        help='Output CSV file path (default: data/{player_id}_games_{season}.csv)'
    )
    args = parser.parse_args()
    fetch_player_games(player_id=args.player_id, season=args.season, output_path=args.output)


if __name__ == '__main__':
    main()
