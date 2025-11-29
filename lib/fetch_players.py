from nba_api.stats.static import players
import pandas as pd
import argparse

from lib.helpers.csv_helpers import write_csv
from lib.helpers.api_wrapper import api_endpoint_wrapper


@api_endpoint_wrapper(max_retries=3, return_empty_df_on_error=True)
def _fetch_players_data() -> pd.DataFrame:
    """
    Internal function to fetch player data from NBA API static data.
    
    Returns:
        DataFrame containing player data
    """
    all_players = players.get_players()
    if all_players:
        return pd.DataFrame(all_players)
    return pd.DataFrame()


def fetch_players(output_path='data/players.csv'):
    """
    Fetch all NBA players and save to CSV.
    
    Args:
        output_path: Path where the CSV file will be saved
        
    Returns:
        DataFrame containing player data
    """
    df = _fetch_players_data()
    
    if df.empty:
        print("No player data found")
        return df
    
    write_csv(df, output_path)
    print(df)
    return df


def main():
    parser = argparse.ArgumentParser(description='Fetch all NBA players and save to CSV')
    parser.add_argument(
        '--output',
        default='data/players.csv',
        help='Output CSV file path (default: data/players.csv)'
    )
    args = parser.parse_args()
    fetch_players(output_path=args.output)


if __name__ == '__main__':
    main()
