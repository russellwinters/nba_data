# CLI refactor plan
Summary
-------
Provide a single, discoverable CLI entrypoint `cli.py` (root) that exposes the project's data-fetching and reporting features via `argparse` subcommands. Move the existing script logic into a `lib/` package and make modules import-safe so the CLI (and programmatic imports) drive execution.

Acceptance criteria
-------------------

- `cli.py --help` lists available subcommands.
- Subcommands exist for: `fetch-players`, `fetch-teams`, `fetch-player-games`, `fetch-team-games`, `fetch-player-stats`, and `read-stats`.
- Existing scripts are moved into `lib/` and expose callable functions; importing modules does not execute network calls or side-effects.
- No hardcoded inputs remain; CLI flags and arguments supply IDs, date ranges, and output paths.
- `README.md` and this file are updated with usage examples and migration notes.

Implementation plan (high-level)
--------------------------------

1. Create `lib/` package and add `__init__.py` that exports the main functions. (Estimate: 20–30m)
2. Move `fetch_players.py`, `fetch_teams.py`, `fetch_player_games.py`, `fetch_team_games.py`, `fetch_player_stats.py`, and `read_stats.py` into `lib/`. Keep filenames but update imports to absolute `lib.` style. (30–45m)
3. Refactor each moved script to expose a small public API (e.g., `fetch_players(...)`) and a `main()` function. Ensure no work runs on import — add `if __name__ == '__main__': main()` guards. (30–60m)
4. Add `cli.py` at the repository root. Implement `argparse` subcommands mapping to the `lib` functions and translate CLI args to function parameters. (30–45m)
5. Replace hardcoded values in the modules with parameters driven by CLI flags; add basic input validation and helpful error messages. (20–40m)
6. Update `README.md` with CLI usage examples and migration notes. (10–20m)

Files to change and rationale
---------------------------

- `cli.py` (new): root entrypoint using `argparse` and subcommands to call `lib` functions.
- `lib/__init__.py` (new): package initializer exporting public functions for the CLI and programmatic use.
- `lib/fetch_players.py`, `lib/fetch_teams.py`, `lib/fetch_player_games.py`, `lib/fetch_team_games.py`, `lib/fetch_player_stats.py`, `lib/read_stats.py`: moved + refactored versions of existing scripts. Rationale: separate library code from CLI and avoid execution on import.
- `README.md`: add quickstart and example `cli.py` invocation(s).

CLI usage examples
------------------

Basic help:

```
python cli.py --help
```

Fetch players (example):

```
python cli.py fetch-players --output data/players.csv
```

Fetch player games by player id and date range (example):

```
python cli.py fetch-player-games --player-id 2544 --start 2022-10-01 --end 2023-04-15 --output data/jokic_games.csv
```

Migration notes
---------------

- After the change, scripts will live under `lib/`. To run the previous behavior directly you can still run `python lib/fetch_players.py` (each module will provide a `main()`), but the preferred flow is `python cli.py <subcommand>`.
- Update any external tooling that executed the old script paths to point to the new locations or to call `cli.py`.

Risks & open questions
----------------------

- Relative imports and file references in the moved scripts must be updated to `lib.` absolute imports; search-and-replace will be required.
- Do you want to support API keys or other configuration via environment variables (e.g., `NBA_API_KEY`) or only CLI flags? Recommendation: support both (flags override env).
- Branching preference: do you want changes on `main` or on a feature branch? Default: create a `feature/cli-refactor` branch.

Next steps
----------

Confirm these choices and where to commit (branch). After confirmation I will: 1) create `lib/` and move/refactor files, 2) add `cli.py` with `argparse`, and 3) update `README.md` and this `docs/plans.md` with final usage examples.
