# Fetch Player Boxscores (by game_id)

One-line summary
-----------------

Fetch individual player box scores for both teams given a `game_id`, and write the player-level data to a CSV file (default output file provided).

Acceptance criteria
-------------------

- The system accepts a single `game_id` string and returns player-level stats for that game.
- Output is written to a default CSV file path unless an alternate `--output` path is provided. By default the output path is `data/player_boxscores.csv` and the tool will overwrite the file if it already exists.
- Player rows include at minimum: `GAME_ID`, `TEAM_ID`, `TEAM_ABBREVIATION`/`teamTricode`, `PLAYER_ID`, `PLAYER_NAME`, `MINUTES`, `PTS`/`points`, `REB`/`reboundsTotal`, `AST`/`assists` — advanced stats are not fetched for this pass.
- The code is implemented inside `lib/fetch_player_boxscores_by_game.py`, with a single function (or small set of functions) that: 1) retrieves traditional box score data for the provided `game_id`, 2) normalizes and merges player rows for both teams into a single DataFrame, and 3) writes the DataFrame to CSV.
- CLI: When invoked with `--game-id <id>` the tool can optionally take `--output <path>` to override the default file path.
- No automated tests required for this first pass (manual verification steps included below).

Proposed implementation plan (high-level tasks)
-----------------------------------------------

1. Add helper function `get_player_boxscores(game_id, timeout=30)` in `lib/fetch_player_boxscores_by_game.py`.
   - Owner: dev (you)
   - Estimate: 1-2 hours
   - Notes: Use the existing `boxscoretraditionalv3.BoxScoreTraditionalV3` (or similar) function to source traditional stats only. Return a single dict or DataFrame with player rows.

2. Add a small normalization step to map column names to a consistent schema.
   - Owner: dev
   - Estimate: 30–60 minutes
   - Notes: Different endpoints use slightly different column names; create a mapping for the output CSV to the canonical columns listed in Acceptance Criteria.

3. Add a CLI flag/behavior to `main()` for writing player-level CSVs.
   - Owner: dev
   - Estimate: 30 minutes
   - Notes: If `--game-id` is provided, call the helper in `lib/fetch_player_boxscores_by_game.py` to fetch player boxscores and write to CSV using the repo's CSV helper (or a small `_write_csv()` helper). Make the default output path `data/player_boxscores.csv`. The tool should overwrite that file by default.

4. Add CSV writing semantics and default output path constant.
   - Owner: dev
   - Estimate: 15 minutes
   - Notes: Add or reuse a `DEFAULT_PLAYER_BOX_SCORES_PATH` constant set to `data/player_boxscores.csv`. Ensure the writer overwrites the file (not append) and creates the `data/` directory if missing.

5. Manual verification and small adjustments.
   - Owner: dev
   - Estimate: 30 minutes
   - Notes: Run the CLI against a known `game_id` and inspect CSV for both teams' players. Iterate on column mapping/formatting if needed.

Files to change
---------------

- `lib/fetch_player_boxscores_by_game.py` — Primary implementation location. Add `get_player_boxscores`, normalization helpers, and CLI wiring. Rationale: keep this new functionality isolated from the existing demo code.
- `lib/__init__.py` — Import the new module so `fetch.py` can import it the same way other fetch modules are exposed.
- `docs/fetch_player_boxscores.md` — (this planning doc) Rationale: central place for plan and follow-up questions.

Suggested tests (deferred)
-------------------------

- None required for this pass per request. When added later, suggested tests:
  - Unit test for `get_player_boxscores()` that mocks NBA API responses and asserts normalized DataFrame shape and column names.
  - Integration/manual test that runs the CLI with a known `game_id` and verifies the CSV file exists and contains rows for two teams.

Manual verification steps
-------------------------

1. Pick a `game_id` known to exist (or from `data/demo_boxscores.csv`) such as `0022400123`.
2. Run the module locally (or run via the top-level `fetch.py` if you wire it in there):

```bash
python lib/fetch_player_boxscores_by_game.py --game-id 0022400123 --output data/player_boxscores.csv
```

3. Open `data/player_boxscores.csv` and confirm:
   - There are player rows for both teams (team identifiers present).
   - Columns include the canonical fields (`GAME_ID`, `PLAYER_ID`, `PLAYER_NAME`, `teamTricode`/`TEAM_ABBREVIATION`, `minutes`, `points`, `reboundsTotal`, `assists`).

Risks and considerations
------------------------

- Column name differences: NBA endpoints sometimes return different column names (e.g., `PTS` vs `points`, `REB` vs `reboundsTotal`). Normalization is required. The canonical column set below should be the CSV output.
- Rate limiting: calling multiple endpoints (traditional + advanced + summary) for many games may trigger rate limits. For a single `game_id` this is fine; consider `delay` between calls for bulk flows.
- Missing/NaN values: some players (DNP) will have missing stat rows; ensure code handles empty DataFrames gracefully.
- File naming: overwriting a single default `data/player_boxscores.csv` may be surprising; consider including `game_id` in the filename by default or document behavior clearly.

Implementation details / suggested column mapping
-----------------------------------------------

- Canonical output column suggestions (CSV column order):
  - `GAME_ID` (string)
  - `PLAYER_ID` (int)
  - `PLAYER_NAME` (string)
  - `TEAM_ID` (int)
  - `teamTricode` or `TEAM_ABBREVIATION` (string)
  - `minutes` or `MIN` (string/decimal)
  - `points` / `PTS` (int)
  - `reboundsTotal` / `REB` (int)
  - `assists` / `AST` (int)
  - `fieldGoalsMade`, `fieldGoalsAttempted`, `fg_pct` (if available)
  - advanced stats (optional): `offensiveRating`, `defensiveRating`, `playerImpactEstimate` (PE if available), etc.

- Normalization approach: build a `COLUMN_MAP` dict mapping known endpoint names to canonical ones, then rename DataFrame columns before concatenation.

Resolved choices
-----------------

- **Implementation file:** `lib/fetch_player_boxscores_by_game.py` (not `lib/demo_boxscores.py`).
- **Default output path:** `data/player_boxscores.csv` (overwritten on each run unless `--output` provided).
- **Columns:** Use the canonical column mapping in this document.
- **Advanced stats:** Not fetched for this pass (no `boxscoreadvancedv3` calls).
- **Usage pattern:** Intended for single-game runs only (no bulk streaming behavior required now).

Follow-up questions (resolved)
-----------------------------

The requester has made these choices; they are reflected above:

1. Filename behavior: default fixed file `data/player_boxscores.csv` (overwrite).
2. Column selection: use the canonical column set listed earlier in this doc.
3. Overwrite vs append: overwrite by default.
4. Advanced stats: not fetched in this pass.
5. Bulk usage: intended for single-game interactive runs for now.

If you'd like, I can implement the change in `lib/demo_boxscores.py` next — confirm the answers to questions 1–4 (or say 'use sensible defaults') and whether to proceed now.
