"""Date formatting helper utilities."""

from datetime import datetime


def format_date_nba(date_str: str) -> str:
    """Convert date string to NBA API format (MM/DD/YYYY).

    The NBA API expects dates in MM/DD/YYYY format, but it's more common
    to work with ISO format dates (YYYY-MM-DD). This helper converts
    between the two formats.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Date in MM/DD/YYYY format. If the input is already in MM/DD/YYYY
        format or is invalid, it is returned unchanged.

    Example:
        >>> from lib.helpers.date_helpers import format_date_nba
        >>> format_date_nba('2024-01-15')
        '01/15/2024'
        >>> format_date_nba('01/15/2024')  # Already in correct format
        '01/15/2024'
    """
    try:
        # datetime.strptime() from Python's standard library parses the string
        # into a datetime object. It raises ValueError if the string doesn't
        # match the expected format pattern.
        # See: https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        # ValueError is raised when the date string doesn't match YYYY-MM-DD format.
        # This means the input is either already in the correct MM/DD/YYYY format
        # or is an invalid date string. In either case, return it unchanged.
        return date_str
