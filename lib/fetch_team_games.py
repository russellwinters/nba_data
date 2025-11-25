from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams
import argparse


def fetch_team_games(team_id: str, season: str, output_path=None):
    """
    Fetch a team's game log for a specific season.
    
    Args:
        team_id: The NBA team abbreviation (e.g., 'PHI', 'LAL')
        season: Season string (e.g., '2018', '2022-23')
        output_path: Optional path where the CSV file will be saved.
                    If None, defaults to 'data/team_{team_id}_games_{season}.csv'
        
    Returns:
        DataFrame containing game data, or None if team not found
    """
    team = teams.find_team_by_abbreviation(team_id)
    if team:
        team_id = team['id']

        # Fetch the team's game log
        regular_season_game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)

        game_data = regular_season_game_log.get_data_frames()[0]
        
        # Write the game data to a CSV file
        if output_path is None:
            output_path = f'data/team_{team_id}_games_{season}.csv'
        game_data.to_csv(output_path, index=False)
        print(game_data)
        return game_data
    else:
        print("Team not found")
        return None


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
