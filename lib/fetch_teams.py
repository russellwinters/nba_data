from nba_api.stats.static import teams
import pandas as pd
import argparse

from lib.helpers.csv_helpers import write_csv
from lib.helpers.api_wrapper import api_endpoint_wrapper


@api_endpoint_wrapper(max_retries=3, return_empty_df_on_error=True)
def _fetch_teams_data() -> pd.DataFrame:
    """
    Internal function to fetch team data from NBA API static data.
    
    Returns:
        DataFrame containing team data
    """
    all_teams = teams.get_teams()
    if all_teams:
        return pd.DataFrame(all_teams)
    return pd.DataFrame()


def fetch_teams(output_path='data/teams.csv'):
    """
    Fetch all NBA teams and save to CSV.
    
    Args:
        output_path: Path where the CSV file will be saved
        
    Returns:
        DataFrame containing team data
    """
    df = _fetch_teams_data()
    
    if df.empty:
        print("No team data found")
        return df
    
    write_csv(df, output_path)
    print(df)
    return df


def main():
    parser = argparse.ArgumentParser(description='Fetch all NBA teams and save to CSV')
    parser.add_argument(
        '--output',
        default='data/teams.csv',
        help='Output CSV file path (default: data/teams.csv)'
    )
    args = parser.parse_args()
    fetch_teams(output_path=args.output)


if __name__ == '__main__':
    main()
