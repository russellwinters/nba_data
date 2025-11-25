from nba_api.stats.static import teams
import pandas as pd
import argparse


def fetch_teams(output_path='data/teams.csv'):
    """
    Fetch all NBA teams and save to CSV.
    
    Args:
        output_path: Path where the CSV file will be saved
        
    Returns:
        DataFrame containing team data
    """
    all_teams = teams.get_teams()
    df = pd.DataFrame(all_teams)
    df.to_csv(output_path, index=False)
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
