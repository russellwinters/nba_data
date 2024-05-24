from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

# Find the player ID for a given player name
player_dict = players.find_players_by_full_name("LeBron James")
if player_dict:
    player_id = player_dict[0]['id']

    # Fetch the career stats
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_stats = career.get_data_frames()[0]

    print(career_stats)
else:
    print("Player not found")

