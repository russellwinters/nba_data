import sys
import pandas as pd

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            data = pd.read_csv(file)
            print(data.to_string())
    except FileNotFoundError:
        print(f"File '{filename}' not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a filename.")
    else:
        filename = sys.argv[1]
        if not filename.endswith('.csv'):
            raise ValueError("Invalid file format. Only CSV files are supported.")
        read_file(f'data/{filename}')