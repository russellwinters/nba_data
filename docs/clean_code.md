# Code Cleanup Initiative

## Overview

This document outlines a planned initiative to improve the code quality, maintainability, and testability of the nba_data repository. The goal is to reduce code duplication, establish consistent patterns, and introduce a test suite that validates functionality without making actual API calls.

## Goals

- **Reduce code duplication** by extracting shared logic into reusable helper modules
- **Improve readability** by establishing consistent error handling patterns across all fetching modules
- **Enable safe testing** by introducing a mock-based test suite that doesn't make real API calls
- **Improve maintainability** by making the codebase easier to understand and modify

## Action Items

### Helper Modules

- [x] Create a `lib/helpers/` directory for shared utility functions
- [x] Extract `_normalize_team_id()` into a shared helper (currently duplicated in `fetch_team_box_scores.py` and `fetch_team_game_logs.py`)
- [x] Create a shared CSV writing utility that handles directory creation, error handling, and consistent logging
- [x] Create a shared date formatting utility (e.g., `_format_date_nba()` from `fetch_team_box_scores.py`)
- [ ] Consider a common base pattern or decorator for API endpoint wrappers that handles timeouts, retries, and error logging

### Shared Error Handling

- [x] Define a consistent error handling strategy across all fetching modules:
  - Decide whether to raise exceptions, return None/empty DataFrames, or use a custom result type
  - Standardize error messages and logging format
- [x] Create custom exception classes for common error scenarios (e.g., `PlayerNotFoundError`, `TeamNotFoundError`, `APIError`)
- [x] Implement a shared error handler that can wrap API calls with consistent try/except patterns
- [ ] Add input validation helpers to validate common parameters (player IDs, team IDs, season strings, dates)

### Testing

- [ ] Set up a test framework (e.g., pytest) in the repository
- [ ] Create mock fixtures for NBA API responses to avoid making actual API calls
- [ ] Add unit tests for helper functions (team ID normalization, date formatting, CSV writing)
- [ ] Add integration tests for each fetching module using mocked API responses
- [ ] Add CLI tests to verify argument parsing and command routing in `fetch.py`
- [ ] Consider using `responses` or `unittest.mock` to mock HTTP requests from `nba_api`
