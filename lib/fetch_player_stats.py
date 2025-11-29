from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import argparse

import pandas as pd

from lib.helpers.csv_helpers import write_csv
from lib.helpers.api_wrapper import api_endpoint_wrapper


@api_endpoint_wrapper(timeout=30, max_retries=3, return_empty_df_on_error=True)
def _fetch_career_stats(player_id: int, timeout: int = 30) -> pd.DataFrame:
    """
    Internal function to fetch player career stats from NBA API.
    
    Args:
        player_id: The NBA player ID
        timeout: Request timeout in seconds
        
    Returns:
        DataFrame containing career stats
    """
    career = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=timeout)
    dfs = career.get_data_frames()
    if dfs:
        return dfs[0]
    return pd.DataFrame()


def fetch_player_stats(player_id: int, output_path=None):
    """
    Fetch a player's career statistics.
    
    Args:
        player_id: The NBA player ID
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/{player_id}_career.csv'
        
    Returns:
        DataFrame containing career stats, or empty DataFrame if player not found
    """
    player = players.find_player_by_id(player_id)
    if player:
        resolved_player_id = player['id']

        # Fetch the career stats using decorated function
        career_stats = _fetch_career_stats(resolved_player_id)
        
        if career_stats.empty:
            print(f"No career stats found for player {player_id}")
            return career_stats
        
        # Write the career stats to a CSV file
        if output_path is None:
            output_path = f'data/{resolved_player_id}_career.csv'
        write_csv(career_stats, output_path)
        print(career_stats)
        return career_stats
    else:
        print("Player not found")
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description='Fetch a player\'s career statistics')
    parser.add_argument(
        '--player-id',
        type=int,
        required=True,
        help='NBA player ID'
    )
    parser.add_argument(
        '--output',
        help='Output CSV file path (default: data/{player_id}_career.csv)'
    )
    args = parser.parse_args()
    fetch_player_stats(player_id=args.player_id, output_path=args.output)


if __name__ == '__main__':
    main()
