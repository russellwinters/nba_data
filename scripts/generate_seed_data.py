#!/usr/bin/env python3
"""
Seed Data Generation Script

This script generates seed data CSV files containing:
1. All NBA players (historical and active)
2. All NBA teams
3. Games and boxscore data from the previous month (or custom date range)
4. Player boxscores (player stats per game)
5. Team boxscores (team stats per game)
6. Player career stats for all players

These CSV files are suitable for database import.

Usage:
    python scripts/generate_seed_data.py
    python scripts/generate_seed_data.py --output-dir custom/path
    python scripts/generate_seed_data.py --date-from 2024-01-01 --date-to 2024-01-31
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path


def create_parser():
    """Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Generate NBA seed data CSV files for database import",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument(
        "--output-dir",
        default="data/seed",
        help="Output directory for CSV files (default: data/seed)",
    )
    
    parser.add_argument(
        "--date-from",
        help="Start date for games (YYYY-MM-DD format). Overrides automatic previous month calculation.",
    )
    
    parser.add_argument(
        "--date-to",
        help="End date for games (YYYY-MM-DD format). Overrides automatic previous month calculation.",
    )
    
    return parser


def calculate_previous_month():
    """
    Calculate the start and end dates of the previous month.
    
    Returns:
        tuple: (start_date, end_date) in YYYY-MM-DD format
        
    Examples:
        - If today is 2024-01-15, returns ('2023-12-01', '2023-12-31')
        - If today is 2024-03-20, returns ('2024-02-01', '2024-02-29')
    """
    today = datetime.now()
    
    # First day of current month
    first_of_month = today.replace(day=1)
    
    # Last day of previous month = day before first of current month
    last_day_prev = first_of_month - timedelta(days=1)
    
    # First day of previous month
    first_day_prev = last_day_prev.replace(day=1)
    
    return (
        first_day_prev.strftime('%Y-%m-%d'),
        last_day_prev.strftime('%Y-%m-%d')
    )


def validate_date_format(date_str):
    """
    Validate that a date string is in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def main():
    """Main entry point for the seed data generation script."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Display configuration
        print("=" * 60)
        print("NBA Seed Data Generation")
        print("=" * 60)
        print(f"Output directory: {args.output_dir}")
        
        # Validate and determine date range
        if args.date_from or args.date_to:
            # Custom date range provided
            if not args.date_from or not args.date_to:
                print("Error: Both --date-from and --date-to must be specified together", file=sys.stderr)
                sys.exit(1)
            
            # Validate date formats
            if not validate_date_format(args.date_from):
                print(f"Error: Invalid date format for --date-from: {args.date_from}", file=sys.stderr)
                print("Expected format: YYYY-MM-DD (e.g., 2024-01-15)", file=sys.stderr)
                sys.exit(1)
            
            if not validate_date_format(args.date_to):
                print(f"Error: Invalid date format for --date-to: {args.date_to}", file=sys.stderr)
                print("Expected format: YYYY-MM-DD (e.g., 2024-01-31)", file=sys.stderr)
                sys.exit(1)
            
            date_from = args.date_from
            date_to = args.date_to
            print(f"Using custom date range: {date_from} to {date_to}")
        else:
            # Calculate previous month automatically
            date_from, date_to = calculate_previous_month()
            print(f"Using previous month date range: {date_from} to {date_to}")
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory ready: {output_path.absolute()}")
        
        print("\nDate Range Calculation:")
        print(f"  Start Date: {date_from}")
        print(f"  End Date:   {date_to}")
        
        # Calculate the number of days in the range
        start_dt = datetime.strptime(date_from, '%Y-%m-%d')
        end_dt = datetime.strptime(date_to, '%Y-%m-%d')
        days_count = (end_dt - start_dt).days + 1
        print(f"  Duration:   {days_count} days")
        
        print("\nPhase 2 complete: Date calculation and validation.")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
