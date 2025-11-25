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

To run the NBA Data CLI, activate the venv and use simple commands, like:

```zsh
python fetch_players.py
```
## Tasks

Check simple [TODO](TODO.md) for task list


## Current Methods:

- **Script —** `fetch_players.py`: Fetches player roster data from an external NBA API, prints a brief summary to stdout, and writes player records to a local CSV (typically `data/players.csv`). Use this to build or refresh the local players dataset.
- **Script —** `fetch_teams.py`: Retrieves team information from the API, prints the results, and can write or update local CSVs with team metadata. Useful for keeping a local reference of teams and their attributes.
- **Script —** `fetch_player_stats.py`: Requests per-player aggregated statistics (season or career level) from the API, prints or returns those stats, and can export them to CSV for analysis.
- **Script —** `fetch_player_games.py`: Downloads game-level data for a specified player (individual game logs), prints sample rows, and can convert or append the game logs to local CSV files for time-series analysis.
- **Script —** `fetch_team_games.py`: Fetches game logs or schedule/results for a specified team, prints key fields, and can save the team game data to CSV for team-level analyses.
- **Utility —** `read_stats.py`: Reads previously saved CSV data (players, teams, stats, or game logs), prints human-readable summaries or filtered views, and helps inspect or validate locally stored datasets.

Notes:
- The descriptions above are concise summaries of each runnable script in the project root. For exact parameters, flags, and outputs, open the corresponding script file (for example, `fetch_players.py`) and review its argument parsing and docstring.


