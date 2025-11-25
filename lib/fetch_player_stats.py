from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import argparse


def fetch_player_stats(player_id: int, output_path=None):
    """
    Fetch a player's career statistics.
    
    Args:
        player_id: The NBA player ID
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/{player_id}_career.csv'
        
    Returns:
        DataFrame containing career stats, or None if player not found
    """
    player = players.find_player_by_id(player_id)
    if player:
        player_id = player['id']

        # Fetch the career stats
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_stats = career.get_data_frames()[0]
        
        # Write the career stats to a CSV file
        if output_path is None:
            output_path = f'data/{player_id}_career.csv'
        career_stats.to_csv(output_path, index=False)
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
