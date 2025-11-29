from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import argparse
import pandas as pd

from lib.helpers.csv_helpers import write_csv
from lib.helpers.validation import validate_player_id
from lib.helpers.api_wrapper import api_endpoint


@api_endpoint(timeout=30)
def _fetch_career_stats(player_id: int) -> pd.DataFrame:
    """Fetch career stats for a player from the NBA API.
    
    Args:
        player_id: The NBA player ID
        
    Returns:
        DataFrame containing career stats
    """
    career = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=30)
    return career.get_data_frames()[0]


def fetch_player_stats(player_id: int, output_path=None):
    """
    Fetch a player's career statistics.
    
    Args:
        player_id: The NBA player ID
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/{player_id}_career.csv'
        
    Returns:
        DataFrame containing career stats, or None if player not found
        
    Raises:
        ValidationError: If player_id is invalid
    """
    # Validate inputs
    player_id = validate_player_id(player_id)
    
    player = players.find_player_by_id(player_id)
    if player:
        player_id = player['id']

        # Fetch the career stats using the decorated function
        career_stats = _fetch_career_stats(player_id)
        
        if career_stats.empty:
            print("Error fetching career stats")
            return None
        
        # Write the career stats to a CSV file
        if output_path is None:
            output_path = f'data/{player_id}_career.csv'
        write_csv(career_stats, output_path)
        print(career_stats)
        return career_stats
    else:
        print("Player not found")
        return None


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
