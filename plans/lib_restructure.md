# Lib Restructure Plan

## Summary

Reorganize the `lib/` package into domain-focused submodules (`player`, `team`, `game`) with co-located, specific modules. Move the CLI logic from `fetch.py` into `lib/` as a `cli.py` module, and introduce a minimal `main.py` at the repository root as the new entrypoint.

## Goals

1. **Co-locate related modules**: Group player-related, team-related, and game-related functionality into their own submodules
2. **Improve discoverability**: Make it clear which domain each module belongs to
3. **Clean entry point**: Have a simple `main.py` at root that delegates to the CLI module in `lib/`
4. **Maintain backward compatibility**: Existing import paths should continue to work via re-exports

## Current Structure

```
nba_data/
├── fetch.py                           # CLI entrypoint (root)
├── lib/
│   ├── __init__.py
│   ├── demo_boxscores.py
│   ├── fetch_player_boxscores_by_game.py
│   ├── fetch_player_games.py
│   ├── fetch_player_stats.py
│   ├── fetch_players.py
│   ├── fetch_team_box_scores.py
│   ├── fetch_team_game_logs.py
│   ├── fetch_team_games.py
│   ├── fetch_teams.py
│   ├── read_stats.py
│   └── helpers/
│       ├── __init__.py
│       └── team_helpers.py
```

## Proposed Structure

```
nba_data/
├── main.py                            # New minimal entrypoint (calls lib.cli)
├── lib/
│   ├── __init__.py                    # Re-exports for backward compatibility
│   ├── cli.py                         # Moved from fetch.py (CLI logic)
│   ├── read_stats.py                  # Utility (stays at lib level)
│   ├── player/
│   │   ├── __init__.py               # Exports: fetch_players, fetch_player_games, etc.
│   │   ├── all.py          # Moved from lib/fetch_players.py
│   │   ├── games_by_season.py     # Moved from lib/fetch_player_games.py
│   │   ├── career_stats.py     # Moved from lib/fetch_player_stats.py
│   ├── team/
│   │   ├── __init__.py               # Exports: fetch_teams, fetch_team_games, etc.
│   │   ├── all.py            # Moved from lib/fetch_teams.py
│   │   ├── games.py       # Moved from lib/fetch_team_games.py
│   ├── game/
│   │   ├── __init__.py               # Exports: boxscores functions
│   │   └── boxscores.py              # Moved from lib/fetch_team_box_scores.py (renamed)
│   └── helpers/
│       ├── __init__.py               # Unchanged
│       └── team_helpers.py           # Unchanged
```

## Actual Repository State (brief)

The implementation in the repository largely follows the proposed restructure (domain submodules and a `lib/cli.py`), but there are a few notable differences from this plan that are important to call out:

- **`lib/__init__.py` exports submodules only**: The package currently imports and exposes the `player`, `team`, and `game` subpackages and the `read_stats` utility. It does *not* perform function-level re-exports (for example, `from lib import fetch_players` will not work). See `lib/__init__.py`.
- **Player boxscore functionality lives in `lib/game`**: Player boxscore functions (the CLI-facing `boxscore` function and `fetch_player_boxscores_by_game` alias) are implemented in `lib/game/boxscore.py` and re-exported from `lib/game/__init__.py`. They are not inside `lib/player/`.
- **Team game lookup implemented as `lib/team/games.py`**: The team game/boxscore finder is `lib/team/games.py` and exposes `games` (aliased as `fetch_team_games`). There is no separate `fetch_team_box_scores.py` module.
- **`main.py` exists and `fetch.py` is not present**: The root `main.py` delegates to `lib.cli.main()` as planned; `fetch.py` has already been removed from the repository.

These differences are deliberate or already committed; the plan file below is updated with these facts in mind (see "Module Categorization" notes and the Acceptance Criteria section).


## Module Categorization

### Player Submodule (`lib/player/`)

| Current File | New Location | Function(s) |
|-------------|--------------|-------------|
| `lib/fetch_players.py` | `lib/player/fetch_players.py` | `fetch_players()` |
| `lib/fetch_player_games.py` | `lib/player/fetch_player_games.py` | `fetch_player_games()` |
| `lib/fetch_player_stats.py` | `lib/player/fetch_player_stats.py` | `fetch_player_stats()` |
| `lib/fetch_player_boxscores_by_game.py` | `lib/player/fetch_player_boxscores.py` | `fetch_player_boxscores_by_game()`, `get_player_boxscores()` |

### Team Submodule (`lib/team/`)

| Current File | New Location | Function(s) |
|-------------|--------------|-------------|
| `lib/fetch_teams.py` | `lib/team/fetch_teams.py` | `fetch_teams()` |
| `lib/fetch_team_games.py` | `lib/team/fetch_team_games.py` | `fetch_team_games()` |
| `lib/fetch_team_game_logs.py` | `lib/team/fetch_team_game_logs.py` | `fetch_team_game_logs()` |
| `lib/fetch_team_box_scores.py` | `lib/team/fetch_team_box_scores.py` | `fetch_team_games()` (note: module provides team game box scores), `write_csv()` |

> **Note**: `lib/fetch_team_box_scores.py` exports `fetch_team_games()` - not `fetch_team_box_scores()`. Consider renaming the function to `fetch_team_box_scores()` during the refactor for consistency, or aliasing it in the `__init__.py`.

### Game Submodule (`lib/game/`)

| Current File | New Location | Function(s) |
|-------------|--------------|-------------|
| `lib/demo_boxscores.py` | `lib/game/boxscores.py` | `find_games_by_team_and_date()`, `find_games_by_date()`, `get_box_score_traditional()`, `get_box_score_advanced()`, `get_game_summary()`, `get_complete_box_score()` |

### CLI Module (`lib/cli.py`)

| Current File | New Location | Description |
|-------------|--------------|-------------|
| `fetch.py` | `lib/cli.py` | CLI argument parsing and subcommand dispatch |

## Implementation Steps

### Phase 1: Create Submodule Structure (No Breaking Changes)

1. **Create submodule directories**
   - Create `lib/player/`, `lib/team/`, `lib/game/` directories
   - Add `__init__.py` files to each submodule

2. **Copy modules to new locations**
   - Copy (don't move yet) each module to its new submodule location
   - Update internal imports within copied modules to use new paths

3. **Update submodule `__init__.py` files**
   - Export all public functions from each submodule
   - Example for `lib/player/__init__.py`:
     ```python
     from .fetch_players import fetch_players
     from .fetch_player_games import fetch_player_games
     from .fetch_player_stats import fetch_player_stats
     from .fetch_player_boxscores import fetch_player_boxscores_by_game, get_player_boxscores
     
     __all__ = [
         'fetch_players',
         'fetch_player_games',
         'fetch_player_stats',
         'fetch_player_boxscores_by_game',
         'get_player_boxscores',
     ]
     ```

### Phase 2: Update Main `lib/__init__.py` for Backward Compatibility

```python
"""
NBA Data Library

This package provides functions for fetching NBA player and team data,
as well as utilities for reading and processing the data.
"""

# Backward-compatible imports - re-export from submodules
from .player import (
    fetch_players,
    fetch_player_games,
    fetch_player_stats,
    fetch_player_boxscores_by_game,
)
from .team import (
    fetch_teams,
    fetch_team_games,
    fetch_team_game_logs,
)
# Import the module for backward compatibility with `from lib import fetch_team_box_scores`
from .team import fetch_team_box_scores
from .game import boxscores
from .read_stats import read_stats

__all__ = [
    'fetch_players',
    'fetch_teams',
    'fetch_player_games',
    'fetch_team_games',
    'fetch_team_game_logs',
    'fetch_player_stats',
    'fetch_player_boxscores_by_game',
    'read_stats',
    'fetch_team_box_scores',  # Module re-export
    'boxscores',
]
```

### Phase 3: Move CLI to lib/cli.py

1. **Create `lib/cli.py`**
   - Move CLI logic from `fetch.py` to `lib/cli.py`
   - Update imports to use new submodule paths (consistent style via submodule `__init__.py`):
     ```python
     from lib.player import (
         fetch_players,
         fetch_player_games,
         fetch_player_stats,
         fetch_player_boxscores_by_game,
     )
     from lib.team import (
         fetch_teams,
         fetch_team_games,
         fetch_team_game_logs,
         fetch_team_box_scores,  # This is the module, not a function
     )
     from lib.read_stats import read_stats
     ```

2. **Create minimal `main.py` at root**
   ```python
   #!/usr/bin/env python3
   """
   NBA Data CLI - Main Entry Point
   
   This module provides the main entry point for the NBA data CLI.
   Run with: python main.py <subcommand> [options]
   """
   
   from lib.cli import main
   
   if __name__ == '__main__':
       main()
   ```

3. **Remove `fetch.py`**
   - Delete `fetch.py` from the repository root
   - No deprecation needed since no MVP has been released

### Phase 4: Clean Up and Remove Old Files

1. Remove original files from `lib/` root (after verification):
   - `lib/fetch_players.py`
   - `lib/fetch_player_games.py`
   - `lib/fetch_player_stats.py`
   - `lib/fetch_player_boxscores_by_game.py`
   - `lib/fetch_teams.py`
   - `lib/fetch_team_games.py`
   - `lib/fetch_team_game_logs.py`
   - `lib/fetch_team_box_scores.py`
   - `lib/demo_boxscores.py`

2. Remove `fetch.py` from repository root (replaced by `main.py`)

## Import Path Changes

### Before
```python
from lib.fetch_players import fetch_players
from lib.fetch_team_games import fetch_team_games
from lib import fetch_team_box_scores
```

### After (New Preferred Style)
```python
from lib.player import fetch_players
from lib.team import fetch_team_games
from lib.team import fetch_team_box_scores
```

### After (Backward Compatible)
```python
# These still work via re-exports in lib/__init__.py
from lib import fetch_players, fetch_team_games
from lib import fetch_team_box_scores  # Module import
```

## Helper Module Import Updates

When modules are moved to submodules, their imports of `lib/helpers/team_helpers.py` need to be updated:

### Before (from lib root)
```python
from lib.helpers.team_helpers import normalize_team_id
```

### After (from submodule - no change needed)
```python
# The import path stays the same because lib/helpers/ is not being moved
from lib.helpers.team_helpers import normalize_team_id
```

> **Note**: Since `lib/helpers/` is staying at the same location, absolute imports like `from lib.helpers.team_helpers import normalize_team_id` will continue to work from any submodule. No changes are required for helper imports.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing imports | Maintain backward-compatible re-exports in `lib/__init__.py` |
| Circular imports | Careful ordering of imports; use absolute imports |
| Helper module path changes | `lib/helpers/` path stays the same; no import changes needed |
| CLI entry point change | Replace `fetch.py` with `main.py`; update documentation |

## Decisions

The following decisions have been made:

1. **Remove `fetch.py`**: Since no MVP has been released, there is no need for a deprecation cycle. The file will be removed entirely and replaced with `main.py`.

2. **Rename `demo_boxscores.py` to `boxscores.py`**: Confirmed. The file will be renamed to `boxscores.py` in the `lib/game/` submodule since it's no longer a demo.

3. **Keep `lib/helpers/` as shared utilities**: Keep the helpers at `lib/helpers/` for now. This can be re-evaluated in the future if helpers become more submodule-specific.

## Acceptance Criteria

- [ ] All modules are organized into `player/`, `team/`, `game/` submodules
- [ ] `lib/cli.py` contains the CLI logic (moved from `fetch.py`)
- [ ] `main.py` at root calls `lib.cli.main()`
- [ ] `fetch.py` is removed from repository root
- [ ] Backward-compatible imports work via `lib/__init__.py`
- [ ] All existing CLI commands work unchanged
- [ ] `python main.py --help` works correctly
- [ ] README.md updated with new structure and usage examples

## Effort Estimate

| Phase | Time |
|-------|------|
| Phase 1: Create submodule structure | 30-45 min |
| Phase 2: Update lib/__init__.py | 15-20 min |
| Phase 3: Move CLI to lib/cli.py | 20-30 min |
| Phase 4: Clean up old files | 10-15 min |
| Testing and validation | 20-30 min |
| Documentation updates | 15-20 min |
| **Total** | **1.5-2.5 hours** |

## Next Steps

1. Review and confirm this plan
2. Create feature branch for implementation
3. Implement phases incrementally with testing after each phase
4. Update README.md and documentation
5. Clean up deprecated files
