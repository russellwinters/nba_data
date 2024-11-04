from nba_api.stats.static import players
import pandas as pd


def main():
    all_players = players.get_players()
    df = pd.DataFrame(all_players)
    df.to_csv('data/players.csv', index=False)
    print(df)

main()