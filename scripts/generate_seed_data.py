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
        
        # Validate date range if provided
        if args.date_from and not args.date_to:
            print("Error: --date-to is required when --date-from is specified", file=sys.stderr)
            sys.exit(1)
        
        if args.date_to and not args.date_from:
            print("Error: --date-from is required when --date-to is specified", file=sys.stderr)
            sys.exit(1)
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory ready: {output_path.absolute()}")
        
        print("\nScript structure initialized successfully.")
        print("Phase 1 complete: Core script structure with CLI parsing.")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
