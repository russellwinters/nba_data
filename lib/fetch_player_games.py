from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import argparse

from lib.helpers.csv_helpers import write_csv
from lib.helpers.validation import validate_player_id, validate_season


def fetch_player_games(player_id: int, season: str, output_path=None):
    """
    Fetch a player's game log for a specific season.
    
    Args:
        player_id: The NBA player ID
        season: Season string (e.g., '2005', '2022-23')
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/{player_id}_games_{season}.csv'
        
    Returns:
        DataFrame containing game data, or None if player not found
        
    Raises:
        ValidationError: If player_id or season is invalid
    """
    # Validate inputs
    player_id = validate_player_id(player_id)
    season = validate_season(season)
    
    player = players.find_player_by_id(player_id)
    if player:
        player_id = player['id']

        # Fetch the player's game log
        regular_season_game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)

        game_data = regular_season_game_log.get_data_frames()[0]
        
        # Write the game data to a CSV file
        if output_path is None:
            output_path = f'data/{player_id}_games_{season}.csv'
        write_csv(game_data, output_path)
        print(game_data)
        return game_data
    else:
        print("Player not found")
        return None


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
