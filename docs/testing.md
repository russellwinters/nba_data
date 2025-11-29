# Testing Documentation

## Overview

This document describes the testing infrastructure for the nba_data repository, including the test framework, mock data strategy, and guidelines for writing tests.

## Test Framework: pytest

### Framework Choice

We use **pytest** as our primary testing framework.

#### Why pytest?

1. **Simplicity and Readability**: pytest uses plain `assert` statements instead of special assertion methods, making tests more readable and easier to write.

2. **Powerful Fixtures**: pytest's fixture system provides a clean way to manage test dependencies, mock data, and setup/teardown logic. Fixtures can be scoped (function, class, module, session) and easily shared across test modules.

3. **Rich Plugin Ecosystem**: pytest has a vast ecosystem of plugins for mocking (`pytest-mock`), coverage (`pytest-cov`), parallel execution (`pytest-xdist`), and more.

4. **Auto-Discovery**: pytest automatically discovers and runs tests based on naming conventions, reducing boilerplate configuration.

5. **Detailed Output**: pytest provides clear, detailed failure messages with context, making debugging easier.

6. **Parametrization**: Built-in support for running the same test with different inputs via `@pytest.mark.parametrize`.

7. **Python Standard**: pytest is the de facto standard for Python testing, with broad community support and documentation.

#### Sources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Python Testing with pytest (Book)](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)

### Alternatives Considered

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **unittest** | Built into Python stdlib; No additional dependencies | More verbose syntax; Less powerful fixtures; Requires class-based tests | Not chosen due to verbosity and less flexible fixture system |
| **nose2** | Successor to nose; Compatible with unittest | Less active development; Smaller community than pytest | Not chosen due to declining popularity and maintenance |
| **doctest** | Tests embedded in docstrings; Good for simple examples | Limited for complex tests; No mocking support; Hard to maintain | Not chosen as primary; May use for documentation examples |

#### Sources for Alternatives

- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [nose2 Documentation](https://docs.nose2.io/)
- [doctest Documentation](https://docs.python.org/3/library/doctest.html)

## Mocking Strategy

### Mock Libraries

We use the following libraries for mocking:

1. **pytest-mock**: A pytest wrapper around `unittest.mock` that provides the `mocker` fixture for easy mocking within tests.

2. **responses**: A library for mocking HTTP requests made with the `requests` library. This is particularly useful for mocking NBA API calls.

#### Sources

- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [responses Documentation](https://github.com/getsentry/responses)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Mock Data Fixtures

Mock data fixtures are defined in `tests/conftest.py` and provide realistic NBA API response data without making actual API calls. This approach:

1. **Avoids Rate Limiting**: The NBA API has rate limits; using mock data prevents hitting these limits during testing.

2. **Ensures Deterministic Tests**: Mock data provides consistent, predictable responses regardless of when tests are run.

3. **Improves Test Speed**: Tests run faster without network I/O.

4. **Enables Offline Testing**: Tests can run without internet connectivity.

### Available Mock Fixtures

| Fixture | Description |
|---------|-------------|
| `mock_teams_list` | List of NBA teams with full metadata |
| `mock_lakers_team` | Single Lakers team record |
| `mock_players_list` | List of NBA players with basic info |
| `mock_lebron_player` | Single LeBron James player record |
| `mock_game_finder_response` | DataFrame matching LeagueGameFinder response |
| `mock_player_game_log_response` | DataFrame matching PlayerGameLog response |
| `mock_player_boxscore_response` | DataFrame matching BoxScoreTraditionalV2 response |
| `mock_empty_dataframe` | Empty DataFrame for edge case testing |
| `mock_empty_game_response` | Empty game response with correct columns |
| `sample_dataframe` | Generic DataFrame for CSV testing |
| `sample_dataframe_with_special_chars` | DataFrame with special characters |

## Project Structure

```
nba_data/
├── tests/
│   ├── __init__.py              # Test package marker
│   ├── conftest.py              # Shared fixtures and mock data
│   ├── test_csv_helpers.py      # Tests for CSV writing utilities
│   ├── test_date_helpers.py     # Tests for date formatting utilities
│   ├── test_fetch_integration.py # Integration tests for fetching modules
│   ├── test_team_helpers.py     # Tests for team ID normalization
│   └── test_validation.py       # Tests for input validation
├── pytest.ini                   # pytest configuration
└── requirements.txt             # Includes test dependencies
```

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests for a specific module
pytest tests/test_date_helpers.py

# Run a specific test function
pytest tests/test_date_helpers.py::test_format_date_nba_valid

# Run tests matching a pattern
pytest -k "date"
```

### Test Output

By default, pytest is configured with:
- Verbose output (`-v`)
- Short tracebacks (`--tb=short`)
- Deprecation warnings filtered

## Writing Tests

### Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
import pytest
from lib.helpers.date_helpers import format_date_nba

def test_format_date_nba_valid():
    """Test conversion from YYYY-MM-DD to MM/DD/YYYY format."""
    result = format_date_nba("2024-01-15")
    assert result == "01/15/2024"

def test_format_date_nba_already_formatted():
    """Test that dates already in NBA format are returned unchanged."""
    result = format_date_nba("01/15/2024")
    assert result == "01/15/2024"

@pytest.mark.parametrize("input_date,expected", [
    ("2024-01-01", "01/01/2024"),
    ("2024-12-31", "12/31/2024"),
    ("2023-06-15", "06/15/2023"),
])
def test_format_date_nba_various_dates(input_date, expected):
    """Test date formatting with various valid dates."""
    assert format_date_nba(input_date) == expected
```

### Using Mock Fixtures

```python
def test_normalize_team_id_with_mock(mock_lakers_team, mocker):
    """Test team ID normalization with mocked API response."""
    # Mock the nba_api teams module
    mocker.patch(
        'lib.helpers.team_helpers.teams.find_team_by_abbreviation',
        return_value=mock_lakers_team
    )
    
    from lib.helpers.team_helpers import normalize_team_id
    
    result = normalize_team_id("LAL")
    assert result == 1610612747
```

## Dependencies

The following packages are required for testing (included in `requirements.txt`):

```
pytest>=8.0.0
pytest-mock>=3.14.0
responses>=0.25.0
```

## Future Enhancements

- [x] Add integration tests for fetching modules with mocked HTTP responses
- [ ] Add CLI tests for argument parsing and command routing
- [ ] Add test coverage reporting with `pytest-cov`
- [ ] Add GitHub Actions workflow for automated testing
