from nba_api.stats.static import teams
import pandas as pd


def main():
    all_teams = teams.get_teams()
    df = pd.DataFrame(all_teams)
    df.to_csv('data/teams.csv', index=False)
    print(df)

main()