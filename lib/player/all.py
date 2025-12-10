from nba_api.stats.static import players
import pandas as pd
import argparse

from lib.helpers.csv_helpers import write_csv


def all(output_path='data/players.csv'):
    """
    Fetch all NBA players and save to CSV.
    
    Args:
        output_path: Path where the CSV file will be saved
        
    Returns:
        DataFrame containing player data
    """
    all_players = players.get_players()
    df = pd.DataFrame(all_players)
    write_csv(df, output_path)
    print(df)
    return df


# Backward compatibility alias
fetch_players = all


def main():
    parser = argparse.ArgumentParser(description='Fetch all NBA players and save to CSV')
    parser.add_argument(
        '--output',
        default='data/players.csv',
        help='Output CSV file path (default: data/players.csv)'
    )
    args = parser.parse_args()
    all(output_path=args.output)


if __name__ == '__main__':
    main()
