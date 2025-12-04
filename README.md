# NBA Data CLI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description

This is a Python command-line interface (CLI) application that fetches NBA data from APIs, prints the data, and converts it to local CSV files.

## Features

- Fetch NBA data from APIs
- Print NBA data
- Convert NBA data to CSV files

## Installation

1. Clone the repository:

   ```zsh
   git clone https://github.com/your-username/nba_proj.git
   ```

2. Install the required dependencies:

   ```zsh
   pip install -r requirements.txt
   ```

## Setup

Follow these steps to create and use a Python virtual environment (macOS, `zsh`):

1. Create a virtual environment in the project root (recommended name: `.venv`).

```zsh
python3 -m venv .venv
```

2. Activate the virtual environment for the current shell session:

```zsh
source .venv/bin/activate
# you should now see `(.venv)` in your prompt
```

3. Install the project dependencies inside the activated venv:

```zsh
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run project scripts and other commands as needed (for example, `python fetch_players.py`).

5. Quick checks and cleanup:

```zsh
pip list                    # list installed packages in the venv
python -c "import requests, pandas; print('ok')"  # quick import smoke-test
deactivate                  # exit the venv when finished
```

## Usage

The NBA Data CLI provides a unified `fetch.py` command with subcommands for all data fetching and reading operations.

### Basic Command Structure

```zsh
python fetch.py <subcommand> [options]
```

### Available Subcommands

- `players` — Fetch all NBA players and save to CSV
- `teams` — Fetch all NBA teams and save to CSV
- `player-games` — Fetch a player's game log for a specific season
- `team-games` — Fetch a team's game log for a specific season
- `player-stats` — Fetch a player's career statistics
- `read-stats` — Read and display a CSV file containing NBA statistics

### Examples

**Get help:**
```zsh
python fetch.py --help                    # See all subcommands
python fetch.py players --help            # Help for a specific subcommand
```

**Fetch all players:**
```zsh
python fetch.py players --output data/players.csv
```

**Fetch all teams:**
```zsh
python fetch.py teams --output data/teams.csv
```

**Fetch player game logs:**
```zsh
python fetch.py player-games --player-id 2544 --season 2022-23
```

**Fetch team game logs:**
```zsh
python fetch.py team-games --team-id LAL --season 2022-23
```

**Fetch player career stats:**
```zsh
python fetch.py player-stats --player-id 2544
```

**Read saved stats:**
```zsh
python fetch.py read-stats players.csv
```
## Tasks

Check docs and plans directories for stuff on the go. This should be organized better.

## Project Structure

The project uses a modular architecture with all core functionality in the `lib/` directory:

- **`fetch.py`** — Unified CLI entrypoint exposing all fetching and reading operations via subcommands
- **`lib/fetch_players.py`** — Player roster data fetching
- **`lib/fetch_teams.py`** — Team information retrieval
- **`lib/fetch_player_stats.py`** — Player career statistics
- **`lib/fetch_player_games.py`** — Player game-level logs
- **`lib/fetch_team_games.py`** — Team game-level logs
- **`lib/read_stats.py`** — CSV data reading and display utility

More detailed feature descriptions can be found on the [Features Doc](./docs/features.md)

For SQL-oriented data modeling of the CSV outputs, see the [Data Model Doc](./docs/data_model.md)