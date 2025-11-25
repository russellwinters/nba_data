import pandas as pd
import argparse


def read_stats(filename, data_dir='data'):
    """
    Read and display a CSV file containing NBA statistics.
    
    Args:
        filename: Name of the CSV file to read
        data_dir: Directory where the file is located (default: 'data')
        
    Returns:
        DataFrame if successful, None if file not found
    """
    if not filename.endswith('.csv'):
        raise ValueError("Invalid file format. Only CSV files are supported.")
    
    filepath = f'{data_dir}/{filename}'
    try:
        data = pd.read_csv(filepath)
        print(data.to_string())
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found in '{data_dir}' directory.")
        return None


def main():
    parser = argparse.ArgumentParser(description='Read and display a CSV file containing NBA statistics')
    parser.add_argument(
        'filename',
        help='Name of the CSV file to read'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Directory where the file is located (default: data)'
    )
    args = parser.parse_args()
    read_stats(filename=args.filename, data_dir=args.data_dir)


if __name__ == "__main__":
    main()
