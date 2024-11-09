from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams


def main(id: int, season: str):
    team = teams.find_team_by_abbreviation(id)
    if team:
        team_id = team['id']

        # Fetch the player's game log
        regular_season_game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)

        game_data = regular_season_game_log.get_data_frames()[0]
        # Write the game data to a CSV file
        game_data.to_csv(f'data/team_{team_id}_games_{season}.csv', index=False)
        print(game_data)
        return game_data
    else:
        print("Player not found")
        return None
    


main('PHI', '2018')