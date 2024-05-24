from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

player = players.find_player_by_id(2544)
if player:
    player_id = player['id']

    # Fetch the career stats
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_stats = career.get_data_frames()[0]
    # Write the 'PLAYER_AGE' column to 'player_age.csv'
    career_stats.to_csv(f'data/{player_id}_career.csv',index=False)
    print(career_stats)
else:
    print("Player not found")

