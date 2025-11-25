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

   ```shell
   git clone https://github.com/your-username/nba_proj.git
   ```

2. Install the required dependencies:

   ```shell
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

4. Example: run the `fetch_players` script:

```zsh
python fetch_players.py
```

5. Quick checks and cleanup:

```zsh
pip list                    # list installed packages in the venv
python -c "import requests, pandas; print('ok')"  # quick import smoke-test
deactivate                  # exit the venv when finished
```



## Usage

To run the NBA Data CLI, use the following command:

## Tasks

Check simple [TODO](TODO.md) for task list
