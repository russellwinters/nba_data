from nba_api.stats.static import teams
import pandas as pd
import argparse

from lib.helpers.csv_helpers import write_csv


def all(output_path='data/teams.csv'):
    """
    Fetch all NBA teams and save to CSV.
    
    Args:
        output_path: Path where the CSV file will be saved
        
    Returns:
        DataFrame containing team data
    """
    all_teams = teams.get_teams()
    df = pd.DataFrame(all_teams)
    write_csv(df, output_path)
    print(df)
    return df


# Backward compatibility alias
fetch_teams = all


def main():
    parser = argparse.ArgumentParser(description='Fetch all NBA teams and save to CSV')
    parser.add_argument(
        '--output',
        default='data/teams.csv',
        help='Output CSV file path (default: data/teams.csv)'
    )
    args = parser.parse_args()
    all(output_path=args.output)


if __name__ == '__main__':
    main()
