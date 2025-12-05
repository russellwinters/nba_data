"""Tests for lib/helpers/date_helpers.py module."""

import pytest

from lib.helpers.date_helpers import format_date_nba


class TestFormatDateNba:
    def test_format_date_nba_valid_iso_format(self):
        """Test conversion from YYYY-MM-DD to MM/DD/YYYY format."""
        result = format_date_nba("2024-01-15")
        assert result == "01/15/2024"

    def test_format_date_nba_beginning_of_year(self):
        result = format_date_nba("2024-01-01")
        assert result == "01/01/2024"

    def test_format_date_nba_end_of_year(self):
        result = format_date_nba("2024-12-31")
        assert result == "12/31/2024"

    def test_format_date_nba_mid_year(self):
        result = format_date_nba("2023-06-15")
        assert result == "06/15/2023"

    def test_format_date_nba_already_nba_format(self):
        result = format_date_nba("01/15/2024")
        assert result == "01/15/2024"

    def test_format_date_nba_invalid_format_returned_unchanged(self):
        result = format_date_nba("15-01-2024")
        assert result == "15-01-2024"

    def test_format_date_nba_empty_string_returned_unchanged(self):
        result = format_date_nba("")
        assert result == ""

    def test_format_date_nba_random_string_returned_unchanged(self):
        result = format_date_nba("not-a-date")
        assert result == "not-a-date"


class TestFormatDateNbaParametrized:
    @pytest.mark.parametrize("input_date,expected", [
        ("2024-01-01", "01/01/2024"),
        ("2024-02-29", "02/29/2024"),  # Leap year
        ("2024-03-15", "03/15/2024"),
        ("2024-04-30", "04/30/2024"),
        ("2024-05-31", "05/31/2024"),
        ("2024-06-15", "06/15/2024"),
        ("2024-07-04", "07/04/2024"),
        ("2024-08-01", "08/01/2024"),
        ("2024-09-30", "09/30/2024"),
        ("2024-10-15", "10/15/2024"),
        ("2024-11-28", "11/28/2024"),
        ("2024-12-25", "12/25/2024"),
    ])
    def test_format_date_nba_all_months(self, input_date, expected):
        assert format_date_nba(input_date) == expected

    @pytest.mark.parametrize("input_date", [
        "2024-13-01",  # Invalid month
        "2024-00-01",  # Invalid month (zero)
        "2024-01-32",  # Invalid day
        "2024-01-00",  # Invalid day (zero)
        "2023-02-29",  # Invalid leap year (2023 not a leap year)
        "abcd-ef-gh",  # Not a date
    ])
    def test_format_date_nba_invalid_dates_returned_unchanged(self, input_date):
        result = format_date_nba(input_date)
        assert result == input_date
