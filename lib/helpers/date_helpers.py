"""Date formatting helper utilities."""

from datetime import datetime


def format_date_nba(date_str: str) -> str:
    """Convert date string to NBA API format (MM/DD/YYYY).

    The NBA API expects dates in MM/DD/YYYY format, but it's more common to
    work with YYYY-MM-DD format in code. This utility handles the conversion.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Date in MM/DD/YYYY format, or the original string if parsing fails

    Example:
        >>> from lib.helpers.date_helpers import format_date_nba
        >>> format_date_nba('2024-01-15')
        '01/15/2024'
        >>> format_date_nba('01/15/2024')  # Already in correct format
        '01/15/2024'
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        # Already in correct format or invalid
        return date_str
