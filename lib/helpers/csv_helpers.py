"""CSV writing helper utilities."""

import os

import pandas as pd


def write_csv(
    df: pd.DataFrame,
    output_path: str,
    *,
    verbose: bool = True,
) -> bool:
    """Write a DataFrame to a CSV file with directory creation and error handling.

    This shared utility provides consistent CSV writing behavior across all
    fetching modules, including:
    - Automatic creation of parent directories
    - Consistent error handling with informative messages
    - Consistent logging of write operations

    Args:
        df: DataFrame to write to CSV
        output_path: Path to the output CSV file
        verbose: If True, print status messages (default: True)

    Returns:
        True if the write was successful, False otherwise

    Example:
        >>> from lib.helpers.csv_helpers import write_csv
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        >>> write_csv(df, 'data/output.csv')
        Wrote 2 rows to data/output.csv
        True
    """
    try:
        # Ensure parent directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        df.to_csv(output_path, index=False)

        if verbose:
            print(f"Wrote {len(df)} rows to {output_path}")

        return True
    except Exception as e:
        if verbose:
            print(f"Error writing to {output_path}: {e}")
        return False
