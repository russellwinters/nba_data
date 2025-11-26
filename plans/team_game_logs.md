# Plan: fetch_team_game_logs

One-line summary
-----------------
Add `lib/fetch_team_game_logs.py` to fetch team game logs using `nba_api.stats.endpoints.teamgamelogs.TeamGameLogs`, supporting a required `team_id` and an optional `season` parameter.

Acceptance criteria (testable)
------------------------------
- Provide function `fetch_team_game_logs(team_id, season=None, *, season_type=None, timeout=30, proxy=None, headers=None, get_request=True)` that returns a `pandas.DataFrame` for valid inputs.
- When `season` is provided, the underlying request parameters include that season (forwarded to `season_nullable`).
- Invalid `team_id` (None or non-int/str) results in a `ValueError` or an empty DataFrame with a warning (consistent with other `lib/fetch_*` modules).
- Docstring, logging, and error handling follow patterns used in existing `lib` modules.

Implementation plan (3–8 tasks)
--------------------------------
1. Create `lib/fetch_team_game_logs.py` (function-based API). Include imports, a small `normalize_team_id` helper, the `fetch_team_game_logs` function, and an example usage in the module docstring. (Owner: dev — 1.5h)
2. Mirror styles from `lib/fetch_player_games.py` / `lib/fetch_team_games.py` for argument names, error handling, and return types. (Owner: dev — 0.5h)
3. Export the function in `lib/__init__.py` so the function is available at package level (confirmed). (Owner: dev — 10m)
4. Update lib/fetch_player_game_logs.py to include arg parser as the other fetch_* files implement. I want optional team_id and season params
5. Update fetch.py to include new fetch_team_game_logs.py and relevant subparser
6. Add a short usage snippet to `game_logs.md` or `docs/features.md` showing how to call the wrapper and pass `season` (Owner: dev — 10m)

Files to change
---------------
- `lib/fetch_team_game_logs.py` — new file: core implementation wrapping `TeamGameLogs` and returning a DataFrame.
- `lib/__init__.py` — update: import and expose `fetch_team_game_logs` at package level (you confirmed this should be exported).
- `game_logs.md` or `docs/features.md` — optional: add a usage example.


Risks & open questions
----------------------
- Network tests can be flaky (rate limits). I recommend unit tests with mocks only when you later want tests.
- Naming: the proposed name `fetch_team_game_logs` is suitable (confirmed).



Next steps
----------
- Confirm: proceed to create `lib/fetch_team_game_logs.py` and update `lib/__init__.py` to export the function.
- If you confirm, I will implement the file, update `lib/__init__.py`, run formatters, and open a follow-up PR (or show the diff here). No tests will be added yet per your instruction.

Status update
-------------
- Step 1 completed: created `lib/fetch_team_game_logs.py` (implementation added).
- Step 2 completed: Updated error handling and argument names to match established patterns.
- Step 3 completed: Update export to include new feature.
- Step 4: Updated file to use parser and follow established patterns
- Step 5: Update fetch.py to include the new fetch_team_game_logs.py file
- Step 6: Usage snippet added to docs/features.md

Generated from `game_logs.md` as the reference for using `TeamGameLogs` and the required parameters.
