# Fetch Team Game Boxscores

One-line summary

- Implement a small fetch module `lib/fetch_team_box_scores.py` that queries a team's games in a given date range (using `LeagueGameFinder`) and writes the same game-list CSV currently produced by `demo_find_games_by_team` (i.e., the contents of `data/demo_boxscores.csv`).

Acceptance criteria

- CLI usage: `python lib/demo_boxscores.py --team-id LAL --date-from 2024-07-01 --date-to 2025-07-01` produces a CSV matching the game-list output format in `data/demo_boxscores.csv`.
- Accepts `team_id` as abbreviation (e.g., `LAL`), full name, numeric string, or numeric team id.
- Supports `--date-from` and `--date-to` (YYYY-MM-DD format). When `--date` is supplied alone, behave like the existing demo and find all games on that date.
- Default CSV output path is `data/demo_boxscores.csv`, overridable with `--output`.
- Graceful handling: unresolved team ids or API errors return an empty DataFrame and print a helpful message.

Scope / Non-goals

- Scope: return the *game list* for the team within the date range (the DataFrame returned by `leaguegamefinder.LeagueGameFinder`), and write that DataFrame to CSV in the same column format used by the demo.
- Non-goals: do not fetch per-game, player-level box scores or aggregate player stats across games.
- Tests: none are required at this time (per request).
- Branching: changes will be made on the current working branch (`demo_agent`) — no new feature branch will be created.
- `lib/demo_boxscores.py` should be left in the repo and explicitly ignored for future changes — the new module will be the canonical fetch implementation.

Proposed implementation (short)

1. Create `lib/fetch_team_box_scores.py` with:
   - `def fetch_team_games(team_id, date_from=None, date_to=None, season=None, timeout=30) -> pandas.DataFrame` that:
     - Reuses `_normalize_team_id` and `_format_date_nba` (adapt from `lib/demo_boxscores.py`) to resolve inputs.
     - Calls `leaguegamefinder.LeagueGameFinder` with `player_or_team_abbreviation='T'` and `team_id_nullable` set to the resolved numeric id; pass `date_from_nullable`, `date_to_nullable`, and `season_nullable` when provided.
     - Returns the first DataFrame from `.get_data_frames()` or an empty DataFrame on error.
   - A helper `_write_csv(df, output_path)` that mirrors the demo's behavior (create parent dir if needed, `df.to_csv(index=False)` and print a summary message).
   - A CLI wrapper (under `if __name__ == '__main__'`) that matches the demo invocation and accepts `--team-id`, `--date`, `--date-from`, `--date-to`, `--season`, and `--output` (default `data/demo_boxscores.csv`). The CLI will call `fetch_team_games()` then write CSV if `--output` is provided.

2. Keep behavior and messaging consistent with `lib/demo_boxscores.py` so users get the same output and messages.

Files to create / change

- Create: `lib/fetch_team_box_scores.py` — core implementation and CLI wrapper. Rationale: centralize the team game-list fetch logic outside the demo file.
- Update: `fetch.py` — add a short note or import line so it can call `lib.fetch_team_box_scores.fetch_team_games` (see example below). Rationale: make `fetch.py` aware of the new module so higher-level scripts can reuse it.
- Do not modify `lib/demo_boxscores.py` (mark it as ignored for this work) — keep the demo file intact for reference.

Integration note for `fetch.py`

Add a short import and call pattern to `fetch.py` so it can use the new function. To match the other fetch docs' style, import the submodule from the `lib` package and call its functions as attributes. Example snippet to add in `fetch.py` where appropriate:

```python
# Example import and usage in fetch.py (package-style submodule import)
from lib import fetch_team_box_scores

# call the fetch function on the submodule:
df = fetch_team_box_scores.fetch_team_games('LAL', date_from='2024-07-01', date_to='2025-07-01')

# then write the CSV using the helper on the submodule:
fetch_team_box_scores._write_csv(df, 'data/demo_boxscores.csv')
```

CLI usage examples

- Find games for a team in a date range and write default CSV:

```bash
python lib/demo_boxscores.py --team-id LAL --date-from 2024-07-01 --date-to 2025-07-01
```

- Find all games on a specific date (demo behavior):

```bash
python lib/demo_boxscores.py --date 2024-01-15
```

Notes and decisions (as requested)

- Output format: the module will reproduce the same DataFrame columns and CSV format produced by `demo_find_games_by_team` in `lib/demo_boxscores.py` (LeagueGameFinder's first DataFrame). If you want post-processing (column selection, renaming, sorting), specify which columns and sort order and I will add that.
- No tests will be added now.
- No new branch will be created; changes can be applied directly to the current branch (`demo_agent`) when you ask me to implement.
- `lib/demo_boxscores.py` is the original demo and should be ignored for new code changes; the new module will be the canonical implementation for production usage.

Next steps (pick one)

- I can implement `lib/fetch_team_box_scores.py` now, commit the file on the current branch (`demo_agent`), and update `fetch.py` with the import snippet above. Say "Proceed" and I will create the file.
- Or I can stop here if you'd prefer to review the plan first.

