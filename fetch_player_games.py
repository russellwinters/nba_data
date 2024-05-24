from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

player = players.find_player_by_id(2544)
season = '2015'
if player:
    player_id = player['id']

    # Fetch the player's game log
    regular_season_game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)

    game_data = regular_season_game_log.get_data_frames()[0]
    # Write the game data to a CSV file
    game_data.to_csv(f'data/{player_id}_games_{season}.csv', index=False)
    print(game_data)
else:
    print("Player not found")
