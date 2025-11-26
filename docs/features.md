# NBA Data Fetch CLI — Feature Documentation

## Overview

The `nba_data` repository provides a unified command-line interface (`fetch.py`) for fetching NBA player, team, and game statistics from the `nba_api` and saving them as CSV files. All functionality is implemented in modular library functions under `lib/` and exposed through a single CLI entry point.

**Architecture**: The repository uses a two-layer design:
1. **Library modules** (`lib/fetch_*.py`, `lib/read_stats.py`): Pure functions that perform fetches, accept parameters, and return DataFrames. Each module can be imported and called programmatically or run standalone with its own CLI.
2. **Unified CLI** (`fetch.py`): A single entry point with subcommands that delegates to library functions, providing consistent argument parsing and error handling across all operations.

**Usage pattern**: `python fetch.py <subcommand> [options]`

---

## Features

### Fetch Players

**Subcommand**: `players`  
**Library module**: `lib/fetch_players.py` → `fetch_players(output_path='data/players.csv')`

**Purpose**: Fetches all NBA players from `nba_api.stats.static.players.get_players()` and saves the result as a CSV while printing the DataFrame to stdout.

**CLI usage**:
```bash
python fetch.py players [--output PATH]
```

**Options**:
- `--output`: Output CSV file path (default: `data/players.csv`)

**Examples**:
```bash
# Fetch players to default location
python fetch.py players

# Fetch to custom path
python fetch.py players --output custom/players_data.csv
```

**Programmatic usage**:
```python
from lib.fetch_players import fetch_players
df = fetch_players(output_path='data/players.csv')
```

**Standalone module usage**:
```bash
python lib/fetch_players.py --output data/players.csv
```

**Outputs**:
- Writes CSV file with player records (columns: id, full_name, first_name, last_name, is_active)
- Prints DataFrame to stdout
- Returns DataFrame on success

**Possible failures**: Network errors, `nba_api` rate limiting, missing `data/` directory or write permissions

---

### Fetch Teams

**Subcommand**: `teams`  
**Library module**: `lib/fetch_teams.py` → `fetch_teams(output_path='data/teams.csv')`

**Purpose**: Fetches all NBA teams from `nba_api.stats.static.teams.get_teams()` and saves the result as a CSV while printing the DataFrame to stdout.

**CLI usage**:
```bash
python fetch.py teams [--output PATH]
```

**Options**:
- `--output`: Output CSV file path (default: `data/teams.csv`)

**Examples**:
```bash
# Fetch teams to default location
python fetch.py teams

# Fetch to custom path
python fetch.py teams --output data/nba_teams.csv
```

**Programmatic usage**:
```python
from lib.fetch_teams import fetch_teams
df = fetch_teams(output_path='data/teams.csv')
```

**Standalone module usage**:
```bash
python lib/fetch_teams.py --output data/teams.csv
```

**Outputs**:
- Writes CSV file with team records (columns: id, full_name, abbreviation, nickname, city, state, year_founded)
- Prints DataFrame to stdout
- Returns DataFrame on success

**Possible failures**: Network errors, `nba_api` rate limiting, filesystem permissions

---

### Fetch Player Career Stats

**Subcommand**: `player-stats`  
**Library module**: `lib/fetch_player_stats.py` → `fetch_player_stats(player_id: int, output_path=None)`

**Purpose**: Fetches career statistics for a single player using `nba_api.stats.endpoints.playercareerstats.PlayerCareerStats`.

**CLI usage**:
```bash
python fetch.py player-stats --player-id <ID> [--output PATH]
```

**Required arguments**:
- `--player-id`: NBA player ID (integer)

**Options**:
- `--output`: Output CSV file path (default: `data/{player_id}_career.csv`)

**Examples**:
```bash
# Fetch career stats for player 2544 (LeBron James)
python fetch.py player-stats --player-id 2544

# Fetch with custom output path
python fetch.py player-stats --player-id 201939 --output data/curry_career.csv
```

**Programmatic usage**:
```python
from lib.fetch_player_stats import fetch_player_stats
df = fetch_player_stats(player_id=2544, output_path='data/lebron_career.csv')
```

**Standalone module usage**:
```bash
python lib/fetch_player_stats.py --player-id 2544 --output data/career.csv
```

**Outputs**:
- Writes `data/{player_id}_career.csv` by default (career stats by season)
- Prints DataFrame to stdout
- Returns DataFrame on success or `None` if player not found

**Possible failures**: Player ID not found (prints "Player not found"), network issues, rate limiting, filesystem write errors

---

### Fetch Player Game Logs

**Subcommand**: `player-games`  
**Library module**: `lib/fetch_player_games.py` → `fetch_player_games(player_id: int, season: str, output_path=None)`

**Purpose**: Fetches a player's per-game statistics for a specific season using `nba_api.stats.endpoints.playergamelog.PlayerGameLog`.

**CLI usage**:
```bash
python fetch.py player-games --player-id <ID> --season <SEASON> [--output PATH]
```

**Required arguments**:
- `--player-id`: NBA player ID (integer)
- `--season`: Season string (e.g., `"2005"`, `"2022-23"`)

**Options**:
- `--output`: Output CSV file path (default: `data/{player_id}_games_{season}.csv`)

**Examples**:
```bash
# Fetch game log for player 2544 in 2022-23 season
python fetch.py player-games --player-id 2544 --season 2022-23

# Fetch with custom output
python fetch.py player-games --player-id 201939 --season 2019 --output data/curry_2019.csv
```

**Programmatic usage**:
```python
from lib.fetch_player_games import fetch_player_games
df = fetch_player_games(player_id=2544, season='2022-23')
```

**Standalone module usage**:
```bash
python lib/fetch_player_games.py --player-id 2544 --season 2022-23
```

**Outputs**:
- Writes `data/{player_id}_games_{season}.csv` by default (game-by-game stats)
- Prints DataFrame to stdout
- Returns DataFrame on success or `None` if player not found

**Possible failures**: Invalid player ID, network/rate-limit errors, filesystem errors

---

### Fetch Team Games

**Subcommand**: `team-games`  
**Library module**: `lib/fetch_team_games.py` → `fetch_team_games(team_id: str, season: str, output_path=None)`

**Purpose**: Fetches a team's game log for a specific season using `nba_api.stats.endpoints.teamgamelog.TeamGameLog`. Team lookup is by abbreviation (e.g., `PHI`, `LAL`).

**CLI usage**:
```bash
python fetch.py team-games --team-id <ABBREVIATION> --season <SEASON> [--output PATH]
```

**Required arguments**:
- `--team-id`: NBA team abbreviation (string, e.g., `"PHI"`, `"LAL"`, `"BOS"`)
- `--season`: Season string (e.g., `"2018"`, `"2022-23"`)

**Options**:
- `--output`: Output CSV file path (default: `data/team_{internal_team_id}_games_{season}.csv`)

**Examples**:
```bash
# Fetch game log for Philadelphia 76ers in 2018
python fetch.py team-games --team-id PHI --season 2018

# Fetch Lakers 2022-23 with custom output
python fetch.py team-games --team-id LAL --season 2022-23 --output data/lakers_2023.csv
```

**Programmatic usage**:
```python
from lib.fetch_team_games import fetch_team_games
df = fetch_team_games(team_id='PHI', season='2018')
```

**Standalone module usage**:
```bash
python lib/fetch_team_games.py --team-id LAL --season 2022-23
```

**Outputs**:
- Writes `data/team_{team_id}_games_{season}.csv` by default (using internal numeric team ID)
- Prints DataFrame to stdout
- Returns DataFrame on success or `None` if team abbreviation not found

**Possible failures**: Invalid team abbreviation (prints "Team not found"), network/rate-limit errors, filesystem errors

---

### Fetch Team Game Logs

**Subcommand**: `team-game-logs`  
**Library module**: `lib/fetch_team_game_logs.py` → `fetch_team_game_logs(team_id, season=None, *, season_type=None, timeout=30, proxy=None, headers=None, get_request=True, output_path=None)`

**Purpose**: Fetches a team's filtered game logs using `nba_api.stats.endpoints.teamgamelog.TeamGameLogs`. The wrapper accepts a flexible `team_id` (numeric internal id, abbreviation like `LAL`, or full team name) and optionally forwards `season` to the endpoint as `season_nullable` and `season_type` where provided. The `output_path` parameter is optional; when omitted the wrapper computes a sensible default CSV path and still writes the DataFrame to disk.

**CLI usage**:
```bash
python fetch.py team-game-logs --team-id <ID|ABBREVIATION|NAME> [--season <SEASON>] [--season-type <TYPE>] [--output PATH]
```

**Required arguments**:
- `--team-id`: Team identifier — numeric id, abbreviation (e.g., `LAL`), or full team name

**Options**:
- `--season`: Season string (e.g., `"2018"`, `"2022-23"`). Optional; forwarded to the endpoint as `season_nullable`
- `--season-type`: Optional season type forwarded to the endpoint (e.g., `"Regular Season"`)
- `--output`: Output CSV file path (optional). If omitted the wrapper will compute a default path (for example: `data/team_{ABBR_or_id}_games_{season}.csv`) and write the CSV there.

**Examples**:
```bash
# Fetch Lakers 2022-23 game logs by abbreviation (writes to default path)
python fetch.py team-game-logs --team-id LAL --season 2022-23

# Fetch by numeric internal team id and save with season-type to a custom path
python fetch.py team-game-logs --team-id 1610612747 --season 2022-23 --season-type "Regular Season" --output data/lakers_2023_logs.csv

# Fetch without season (season is optional)
python fetch.py team-game-logs --team-id PHI
```

**Programmatic usage**:
```python
from lib.fetch_team_game_logs import fetch_team_game_logs

# By abbreviation; omitting output_path writes to a default CSV path
df = fetch_team_game_logs(team_id='LAL', season='2022-23')

# Explicitly provide an output path if you want a custom location
df = fetch_team_game_logs(team_id=1610612747, output_path='data/lakers_2023_logs.csv')
```

**Standalone module usage**:
```bash
python lib/fetch_team_game_logs.py --team-id LAL --season 2022-23 --season-type "Regular Season" [--output data/custom.csv]
```

**Outputs**:
- Returns a `pandas.DataFrame` containing the filtered game logs
- The wrapper writes a CSV to disk: if `output_path`/`--output` is provided it writes there; if omitted it computes and writes to a default path (e.g., `data/team_{ABBR_or_id}_games_{season}.csv`)
- Returns an empty DataFrame for invalid inputs (the wrapper is tolerant and uses empty DataFrames to indicate no data)

**Possible failures**: Invalid `team_id` (ValueError or empty DataFrame), network/rate-limit errors, filesystem/write errors

---

### Read Stats (CSV Viewer)

**Subcommand**: `read-stats`  
**Library module**: `lib/read_stats.py` → `read_stats(filename, data_dir='data')`

**Purpose**: Reads and displays a CSV file from the `data/` directory (or custom directory) using pandas' `to_string()` for readable console output.

**CLI usage**:
```bash
python fetch.py read-stats <FILENAME> [--data-dir PATH]
```

**Required arguments**:
- `filename`: Name of the CSV file to read (must end with `.csv`)

**Options**:
- `--data-dir`: Directory where the file is located (default: `data`)

**Examples**:
```bash
# Read players CSV from default data/ directory
python fetch.py read-stats players.csv

# Read from custom directory
python fetch.py read-stats teams.csv --data-dir custom_data/
```

**Programmatic usage**:
```python
from lib.read_stats import read_stats
df = read_stats(filename='players.csv', data_dir='data')
```

**Standalone module usage**:
```bash
python lib/read_stats.py players.csv --data-dir data
```

**Outputs**:
- Prints CSV contents to stdout (formatted with pandas)
- Returns DataFrame on success or `None` if file not found

**Validation**:
- Raises `ValueError` if filename doesn't end with `.csv`
- Prints `"File '<filename>' not found in '<data_dir>' directory."` if file doesn't exist

---

## Environment & Dependencies

**Virtual environment setup**:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Dependencies**: 
- `nba_api`: Provides NBA statistics endpoints
- `pandas`: Data manipulation and CSV operations

**Network requirements**: All fetch operations require network access to NBA Stats API. You may encounter rate limits or network errors during fetching.

**File system**: CSV outputs are written to the `data/` directory by default (ensure it exists and is writable).

---

## References

**Library modules**:
- `lib/fetch_players.py`: Player list fetching[1]
- `lib/fetch_teams.py`: Team list fetching[1]
- `lib/fetch_player_stats.py`: Player career statistics[1]
- `lib/fetch_player_games.py`: Player game logs[1]
- `lib/fetch_team_games.py`: Team game logs[1]
- `lib/read_stats.py`: CSV file reader[1]

**Unified CLI**: `fetch.py`: Single entry point with subcommand architecture[1]

---

[1] Source files in this repository: `/Users/russellwinters/Developer/projects/nba_data/`

