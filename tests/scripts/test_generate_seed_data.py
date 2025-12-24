"""Tests for scripts/generate_seed_data.py module."""

from datetime import datetime
from unittest.mock import patch

import pytest

# Import functions from the script
import sys
sys.path.insert(0, 'scripts')
from generate_seed_data import calculate_previous_month, validate_date_format


class TestCalculatePreviousMonth:
    """Test suite for calculate_previous_month function."""
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_january(self, mock_datetime):
        """Test calculation when current month is January."""
        # If today is Jan 15, 2024, previous month should be Dec 1-31, 2023
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2023-12-01"
        assert end_date == "2023-12-31"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_february(self, mock_datetime):
        """Test calculation when current month is February."""
        # If today is Feb 20, 2024, previous month should be Jan 1-31, 2024
        mock_datetime.now.return_value = datetime(2024, 2, 20)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2024-01-01"
        assert end_date == "2024-01-31"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_march(self, mock_datetime):
        """Test calculation for February (leap year)."""
        # If today is Mar 20, 2024, previous month should be Feb 1-29, 2024 (leap year)
        mock_datetime.now.return_value = datetime(2024, 3, 20)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2024-02-01"
        assert end_date == "2024-02-29"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_non_leap_year_february(self, mock_datetime):
        """Test calculation for February (non-leap year)."""
        # If today is Mar 10, 2023, previous month should be Feb 1-28, 2023 (non-leap year)
        mock_datetime.now.return_value = datetime(2023, 3, 10)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2023-02-01"
        assert end_date == "2023-02-28"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_april(self, mock_datetime):
        """Test calculation for March (31 days)."""
        # If today is Apr 5, 2024, previous month should be Mar 1-31, 2024
        mock_datetime.now.return_value = datetime(2024, 4, 5)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2024-03-01"
        assert end_date == "2024-03-31"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_may(self, mock_datetime):
        """Test calculation for April (30 days)."""
        # If today is May 15, 2024, previous month should be Apr 1-30, 2024
        mock_datetime.now.return_value = datetime(2024, 5, 15)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2024-04-01"
        assert end_date == "2024-04-30"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_end_of_month(self, mock_datetime):
        """Test calculation when current day is at end of month."""
        # If today is Jan 31, 2024, previous month should be Dec 1-31, 2023
        mock_datetime.now.return_value = datetime(2024, 1, 31)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2023-12-01"
        assert end_date == "2023-12-31"
    
    @patch('generate_seed_data.datetime')
    def test_calculate_previous_month_beginning_of_month(self, mock_datetime):
        """Test calculation when current day is first of month."""
        # If today is Apr 1, 2024, previous month should be Mar 1-31, 2024
        mock_datetime.now.return_value = datetime(2024, 4, 1)
        mock_datetime.strptime = datetime.strptime
        
        start_date, end_date = calculate_previous_month()
        
        assert start_date == "2024-03-01"
        assert end_date == "2024-03-31"


class TestValidateDateFormat:
    """Test suite for validate_date_format function."""
    
    def test_validate_date_format_valid_dates(self):
        """Test validation of valid date formats."""
        assert validate_date_format("2024-01-15") is True
        assert validate_date_format("2024-12-31") is True
        assert validate_date_format("2024-02-29") is True  # Leap year
        assert validate_date_format("2023-06-15") is True
    
    def test_validate_date_format_invalid_formats(self):
        """Test validation of invalid date formats."""
        assert validate_date_format("01/15/2024") is False  # Wrong format
        assert validate_date_format("15-01-2024") is False  # Wrong format
        assert validate_date_format("2024/01/15") is False  # Wrong format
        assert validate_date_format("January 15, 2024") is False
    
    def test_validate_date_format_invalid_dates(self):
        """Test validation of invalid dates."""
        assert validate_date_format("2024-13-01") is False  # Invalid month
        assert validate_date_format("2024-00-01") is False  # Invalid month
        assert validate_date_format("2024-01-32") is False  # Invalid day
        assert validate_date_format("2024-01-00") is False  # Invalid day
        assert validate_date_format("2023-02-29") is False  # Not a leap year
    
    def test_validate_date_format_edge_cases(self):
        """Test validation of edge cases."""
        assert validate_date_format("") is False
        assert validate_date_format("not-a-date") is False
        assert validate_date_format("2024") is False
        assert validate_date_format("2024-01") is False


class TestDateFormatParametrized:
    """Parametrized tests for date validation."""
    
    @pytest.mark.parametrize(
        "date_str",
        [
            "2024-01-01",
            "2024-02-29",  # Leap year
            "2024-03-31",
            "2024-04-30",
            "2024-05-31",
            "2024-06-30",
            "2024-07-31",
            "2024-08-31",
            "2024-09-30",
            "2024-10-31",
            "2024-11-30",
            "2024-12-31",
        ],
    )
    def test_valid_dates_all_months(self, date_str):
        """Test validation of valid dates across all months."""
        assert validate_date_format(date_str) is True
    
    @pytest.mark.parametrize(
        "date_str",
        [
            "01/01/2024",
            "2024/01/01",
            "01-01-2024",
            "January 1, 2024",
            "2024-13-01",
            "2024-00-15",
            "2024-01-32",
            "2023-02-29",  # Non-leap year
            "not a date",
            "",
        ],
    )
    def test_invalid_dates_various_formats(self, date_str):
        """Test validation of invalid dates and formats."""
        assert validate_date_format(date_str) is False
