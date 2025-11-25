**Fetch Players**
- **File**: `fetch_players.py` : Pulls the canonical player list from `nba_api` and writes it to `data/players.csv`.
- **Purpose**: Fetches all NBA players from `nba_api.stats.static.players.get_players()` and saves the result as a CSV while printing the DataFrame to stdout.
- **Required args**: None (the script runs `main()` with no args).
- **How it's called (existing script)**: `python fetch_players.py` — the file calls `main()` at module import, so running the file executes the fetch.
- **Example (venv)**:
  - Activate virtualenv: `source venv/bin/activate`
  - Run: `python fetch_players.py`
- **Outputs**:
  - Writes `data/players.csv` (CSV of player records).
  - Prints the pandas DataFrame representation of all players to stdout.
  - Possible failures: network errors, `nba_api` rate limiting, missing `data/` directory write-permissions.

**Fetch Teams**
- **File**: `fetch_teams.py` : Pulls the canonical team list from `nba_api` and writes it to `data/teams.csv`.
- **Purpose**: Fetches all NBA teams from `nba_api.stats.static.teams.get_teams()` and saves the result as a CSV while printing the DataFrame to stdout.
- **Required args**: None.
- **How it's called (existing script)**: `python fetch_teams.py` — runs `main()` at module import.
- **Example (venv)**:
  - `source venv/bin/activate`
  - `python fetch_teams.py`
- **Outputs**:
  - Writes `data/teams.csv` (CSV of team records).
  - Prints the pandas DataFrame of teams to stdout.
  - Possible failures: same as above (network, rate limits, filesystem permissions).

**Fetch Player Career Stats**
- **File**: `fetch_player_stats.py` : Fetches career statistics for a single player and writes them to CSV.
- **Purpose**: Uses `nba_api.stats.endpoints.playercareerstats.PlayerCareerStats` to retrieve career stats for a player identified by numeric player ID.
- **Function signature**: `main(id: int)` — expects an integer NBA player id.
- **How it's called (existing script)**: The file currently calls `main(2554)` at the bottom, so `python fetch_player_stats.py` will fetch for player id `2554`.
- **How to call programmatically**: Import and call: `from fetch_player_stats import main; main(201939)` (replace `201939` with desired player id).
- **Example (venv)**:
  - `source venv/bin/activate`
  - `python fetch_player_stats.py` (uses hard-coded `main(2554)` in this repo state)
- **Outputs**:
  - Writes `data/{player_id}_career.csv` (e.g., `data/2554_career.csv`) containing the career stats DataFrame.
  - Prints the career stats DataFrame to stdout.
  - Returns the pandas DataFrame on success or `None` if player not found.
  - Possible failures: player id not found (prints "Player not found"), network issues, rate limiting, filesystem write errors.

**Fetch Player Game Logs**
- **File**: `fetch_player_games.py` : Fetches a player's game log for a given season and writes it to CSV.
- **Purpose**: Uses `nba_api.stats.endpoints.playergamelog.PlayerGameLog` to get per-game data for a player in a season.
- **Function signature**: `main(id: int, season: str)` — `id` is numeric player id, `season` is a season string (the script uses values like `'2005'`).
- **How it's called (existing script)**: The file currently calls `main(2544, '2005')` at the bottom, so `python fetch_player_games.py` will fetch that player's 2005 game log.
- **How to call programmatically**: `from fetch_player_games import main; main(2544, '2019')`.
- **Example (venv)**:
  - `source venv/bin/activate`
  - `python fetch_player_games.py` (runs the hard-coded sample)
- **Outputs**:
  - Writes `data/{player_id}_games_{season}.csv` (e.g., `data/2544_games_2005.csv`).
  - Prints the game log DataFrame to stdout.
  - Returns the DataFrame on success or `None` (and prints "Player not found") if the player id lookup fails.
  - Possible failures: invalid player id, network/rate-limit, filesystem errors.

**Fetch Team Game Logs**
- **File**: `fetch_team_games.py` : Fetches a team's game log for a given season and writes it to CSV.
- **Purpose**: Uses `nba_api.stats.endpoints.teamgamelog.TeamGameLog` with a lookup by abbreviation (e.g., `PHI`) to get team game logs for a season.
- **Function signature**: `main(id: str, season: str)` — `id` should be a team abbreviation (e.g., `'PHI'`), `season` is a season string.
- **How it's called (existing script)**: The file currently calls `main('PHI', '2018')` at the bottom; running `python fetch_team_games.py` executes that sample.
- **How to call programmatically**: `from fetch_team_games import main; main('LAL', '2019')`.
- **Example (venv)**:
  - `source venv/bin/activate`
  - `python fetch_team_games.py`
- **Outputs**:
  - Writes `data/team_{team_id}_games_{season}.csv` (team internal id used, e.g., `data/team_1610612755_games_2018.csv`).
  - Prints the team game log DataFrame to stdout.
  - Returns the DataFrame on success or `None` (and prints "Player not found") if team lookup fails.
  - Possible failures: invalid abbreviation (lookup fails), network/rate-limit, filesystem errors.

**Read Stats (CSV viewer)**
- **File**: `read_stats.py` : Simple CSV viewer that prints a CSV from `data/` to stdout.
- **Purpose**: Reads a CSV file from the repository `data/` directory and prints it with pandas' `to_string()` for readable console output.
- **How it's called (CLI)**: `python read_stats.py <filename.csv>` — the script will prepend `data/`, so pass a CSV filename (e.g., `players.csv`).
- **Example (venv)**:
  - `source venv/bin/activate`
  - `python read_stats.py players.csv`  # prints `data/players.csv`
- **Required args**: One positional argument: filename (must end with `.csv`). If no argument is provided, the script prints `Please provide a filename.` and exits.
- **Behavior / Outputs**:
  - On success: prints the CSV contents to stdout using pandas.
  - If the file doesn't exist: prints `File '<filename>' not found.` (the script attempts to open `data/<filename>`).
  - If the argument doesn't end with `.csv`: raises `ValueError("Invalid file format. Only CSV files are supported.")`.

**Notes & Environment**
- **Dependencies**: These scripts use `nba_api` and `pandas`. Ensure your virtual environment has packages installed (see `requirements.txt`).
- **Network**: `nba_api` calls require network access; you may hit rate limits or experience network errors when fetching.
- **Data directory**: CSV outputs are written to the repository `data/` directory (ensure it exists and is writable).
- **Calling with different inputs**: Most scripts define `main(...)` with parameters but call `main(...)` directly at module import with fixed example inputs; to run with different inputs either modify the bottom `main(...)` call or import the `main` function in another script or REPL and pass your arguments.

---

References
- Source scripts in this repo: `fetch_players.py`, `fetch_teams.py`, `fetch_player_stats.py`, `fetch_player_games.py`, `fetch_team_games.py`, `read_stats.py`.
