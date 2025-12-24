# Seed Data Generation Script Plan

## Problem Statement

Create a script that generates seed data CSV files containing:
1. All NBA players (historical and active)
2. All NBA teams
3. Games and boxscore data from the previous month
4. Player boxscores (player stats per game)
5. Team boxscores (team stats per game)
6. Player career stats for all players

These CSV files will be used in a separate application to load/parse data into a relational database.

## Objective

Develop a command-line script that:
- Fetches comprehensive NBA data using existing library modules
- Generates well-structured CSV files suitable for database import
- Handles date calculations automatically (previous month date range)
- Provides clear feedback on the data collection process
- Follows the existing project conventions and patterns

## Current State Analysis

### Existing Functionality

The project already has robust data fetching capabilities:

#### 1. Player Data (`lib/player/all.py`)
- Function: `all(output_path='data/players.csv')`
- Fetches all NBA players using `nba_api.stats.static.players.get_players()`
- Returns DataFrame with columns: `id`, `full_name`, `first_name`, `last_name`, `is_active`
- Already writes to CSV using shared `write_csv()` helper

#### 2. Team Data (`lib/team/all.py`)
- Function: `all(output_path='data/teams.csv')`
- Fetches all NBA teams using `nba_api.stats.static.teams.get_teams()`
- Returns DataFrame with columns: `id`, `full_name`, `abbreviation`, `nickname`, `city`, `state`, `year_founded`
- Already writes to CSV using shared `write_csv()` helper

#### 3. Player Career Stats (`lib/player/career_stats.py`)
- Function: `career_stats(player_id, output_path=None)`
- Fetches career statistics for a single player using `PlayerCareerStats` endpoint
- Returns DataFrame with season-by-season statistics
- Already writes to CSV using shared `write_csv()` helper

#### 4. Game/Boxscore Data (`lib/game/boxscores.py`)
- Function: `find_games_by_team_and_date()` - Uses LeagueGameFinder endpoint
- Function: `find_games_by_date()` - Uses ScoreboardV2 endpoint  
- Function: `get_box_score_traditional()` - Gets player stats for a specific game
- Function: `get_complete_box_score()` - Combines multiple endpoints for comprehensive game data
- Returns both player_stats and team_stats DataFrames

#### 5. Helper Utilities
- `lib/helpers/csv_helpers.py` - `write_csv()` for consistent CSV output
- `lib/helpers/date_helpers.py` - `format_date_nba()` for date format conversion
- `lib/helpers/team_helpers.py` - Team ID normalization
- `lib/helpers/api_wrapper.py` - API call wrapper with timeout handling

### Gaps to Address

1. **No unified seed data script** - Currently each data type requires separate CLI invocation
2. **No automatic date range calculation** - User must manually specify "previous month" dates
3. **No comprehensive game collection** - Need to fetch games across all teams for a date range
4. **No player boxscore aggregation** - Need to collect player stats for all games found
5. **No team boxscore aggregation** - Need to collect team stats for all games found
6. **No bulk player career stats fetching** - Need to fetch career stats for all players

## Technical Approach

### Script Design

Create a new script: `scripts/generate_seed_data.py`

**Key Features:**
- Standalone executable script (can be run independently)
- Also callable as a module from CLI
- Automatic "previous month" date calculation
- Progress indicators for long-running operations
- Configurable output directory
- Error handling with graceful degradation

### Architecture

```
generate_seed_data.py
├── calculate_previous_month() → returns (start_date, end_date)
├── fetch_players_data() → writes players.csv
├── fetch_teams_data() → writes teams.csv
├── fetch_player_career_stats_data() → writes player_career_stats.csv
│   ├── Gets all players
│   ├── For each player, fetches career stats
│   └── Aggregates all career stats
├── fetch_games_data() → writes games.csv
│   ├── Iterates through each day in date range
│   ├── For each day, calls find_games_by_date()
│   └── Deduplicates and aggregates all games
├── fetch_player_boxscores_data() → writes player_boxscores.csv
│   ├── Uses game IDs from games.csv
│   ├── For each game, fetches player boxscores
│   └── Aggregates all player stats
└── fetch_team_boxscores_data() → writes team_boxscores.csv
    ├── Uses game IDs from games.csv
    ├── For each game, fetches team boxscores
    └── Aggregates all team stats

main()
├── Parse CLI arguments
├── Calculate date range
├── Fetch all data types
└── Report summary
```

### Date Range Calculation

```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def calculate_previous_month():
    """
    Calculate the start and end dates of the previous month.
    
    Returns:
        tuple: (start_date, end_date) in YYYY-MM-DD format
        
    Examples:
        - If today is 2024-01-15, returns ('2023-12-01', '2023-12-31')
        - If today is 2024-03-20, returns ('2024-02-01', '2024-02-29')
    """
    today = datetime.now()
    
    # First day of current month
    first_of_month = today.replace(day=1)
    
    # Last day of previous month = day before first of current month
    last_day_prev = first_of_month - timedelta(days=1)
    
    # First day of previous month
    first_day_prev = last_day_prev.replace(day=1)
    
    return (
        first_day_prev.strftime('%Y-%m-%d'),
        last_day_prev.strftime('%Y-%m-%d')
    )
```

### Data Collection Strategy

#### 1. Players and Teams (Simple)
- Direct call to existing `lib.player.all()` and `lib.team.all()`
- No additional processing needed

#### 2. Games Collection (Complex)
**Challenge:** Need all games in a date range without duplication

**Solution (Preferred):**
```python
from datetime import datetime, timedelta

def fetch_games_data(date_from, date_to, output_path):
    """
    Fetch all games in the date range by iterating through each day.
    
    Strategy:
    1. Parse start and end dates
    2. For each day in the range, use find_games_by_date()
    3. Collect all game records
    4. Deduplicate by GAME_ID (just in case)
    5. Write unique games to CSV
    """
    start_date = datetime.strptime(date_from, '%Y-%m-%d')
    end_date = datetime.strptime(date_to, '%Y-%m-%d')
    
    all_games = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"Fetching games for {date_str}...")
        
        # Find games for this date
        games_df = find_games_by_date(date_str)
        if not games_df.empty:
            all_games.append(games_df)
        
        time.sleep(0.5)  # Rate limiting between requests
        current_date += timedelta(days=1)
    
    # Combine and deduplicate
    if all_games:
        combined = pd.concat(all_games, ignore_index=True)
        unique_games = combined.drop_duplicates(subset=['GAME_ID'])
        write_csv(unique_games, output_path)
        return unique_games
    
    return pd.DataFrame()
```

This approach is more efficient than iterating through teams because:
- Games are only returned once per day (not once per team)
- Fewer API calls overall (number of days vs number of teams × games per team)
- Natural deduplication by date

#### 3. Player Boxscore Collection (Complex)
**Challenge:** Need player boxscores for all games found

**Solution:**
```python
def fetch_player_boxscores_data(games_df, output_path):
    """
    Fetch player boxscores for all games.
    
    Args:
        games_df: DataFrame with GAME_ID column
        output_path: Path for player boxscores CSV
    """
    all_boxscores = []
    total_games = len(games_df['GAME_ID'].unique())
    
    for i, game_id in enumerate(games_df['GAME_ID'].unique(), 1):
        print(f"Fetching player boxscores: {i}/{total_games} games")
        result = get_box_score_traditional(game_id)
        if not result['player_stats'].empty:
            all_boxscores.append(result['player_stats'])
        time.sleep(0.5)  # Rate limiting
    
    # Combine all boxscores
    if all_boxscores:
        combined = pd.concat(all_boxscores, ignore_index=True)
        write_csv(combined, output_path)
        return combined
    
    return pd.DataFrame()
```

#### 4. Team Boxscore Collection (Complex)
**Challenge:** Need team stats for all games found

**Solution:**
```python
def fetch_team_boxscores_data(games_df, output_path):
    """
    Fetch team boxscores for all games.
    
    Args:
        games_df: DataFrame with GAME_ID column
        output_path: Path for team boxscores CSV
    """
    all_team_stats = []
    total_games = len(games_df['GAME_ID'].unique())
    
    for i, game_id in enumerate(games_df['GAME_ID'].unique(), 1):
        print(f"Fetching team boxscores: {i}/{total_games} games")
        result = get_box_score_traditional(game_id)
        if not result['team_stats'].empty:
            all_team_stats.append(result['team_stats'])
        time.sleep(0.5)  # Rate limiting (can reuse same call as player boxscores)
    
    # Combine all team stats
    if all_team_stats:
        combined = pd.concat(all_team_stats, ignore_index=True)
        write_csv(combined, output_path)
        return combined
    
    return pd.DataFrame()
```

#### 5. Player Career Stats Collection (Complex)
**Challenge:** Need career stats for all players

**Solution:**
```python
def fetch_player_career_stats_data(output_path):
    """
    Fetch career stats for all players.
    
    Strategy:
    1. Get all players using lib.player.all()
    2. For each player, fetch career stats
    3. Aggregate all career records
    4. Write to CSV
    """
    # Get all players
    players_df = players.get_players()
    all_career_stats = []
    total_players = len(players_df)
    
    for i, player in enumerate(players_df.itertuples(), 1):
        if i % 100 == 0:  # Progress every 100 players
            print(f"Fetching career stats: {i}/{total_players} players")
        
        try:
            career_df = _fetch_career_stats(player.id)
            if not career_df.empty:
                all_career_stats.append(career_df)
        except Exception as e:
            # Skip players with no stats (e.g., very old players)
            continue
        
        time.sleep(0.5)  # Rate limiting
    
    # Combine all career stats
    if all_career_stats:
        combined = pd.concat(all_career_stats, ignore_index=True)
        write_csv(combined, output_path)
        return combined
    
    return pd.DataFrame()
```

### Output File Structure

```
data/seed/
├── players.csv               # All players
├── teams.csv                 # All teams
├── player_career_stats.csv   # Career stats for all players
├── games.csv                 # All games from previous month
├── player_boxscores.csv      # Player boxscores for those games
└── team_boxscores.csv        # Team boxscores for those games
```

#### CSV Schemas

**players.csv:**
```
id,full_name,first_name,last_name,is_active
203999,Nikola Jokic,Nikola,Jokic,true
...
```

**teams.csv:**
```
id,full_name,abbreviation,nickname,city,state,year_founded
1610612747,Los Angeles Lakers,LAL,Lakers,Los Angeles,California,1948
...
```

**player_career_stats.csv:**
```
PLAYER_ID,SEASON_ID,LEAGUE_ID,TEAM_ID,TEAM_ABBREVIATION,PLAYER_AGE,GP,GS,MIN,FGM,FGA,...
203999,2023-24,00,1610612743,DEN,28,79,79,34.6,9.7,16.5,...
...
```

**games.csv:**
```
GAME_ID,GAME_DATE,HOME_TEAM_ID,VISITOR_TEAM_ID,GAME_STATUS_TEXT,...
0022300123,2024-01-15,1610612747,1610612738,Final,...
...
```

**player_boxscores.csv:**
```
personId,playerName,teamTricode,points,reboundsTotal,assists,minutes,gameId,...
203999,Nikola Jokic,DEN,27,12,8,36:24,0022300123,...
...
```

**team_boxscores.csv:**
```
teamId,teamName,teamCity,teamTricode,points,reboundsTotal,assists,fieldGoalsPercentage,...
1610612743,Nuggets,Denver,DEN,115,48,28,0.487,...
...
```

## Implementation Plan

### Phase 1: Core Script Structure
1. Create `scripts/` directory if it doesn't exist
2. Create `scripts/generate_seed_data.py` with:
   - Argument parser (output directory, custom date range options)
   - Main execution flow
   - Progress reporting

### Phase 2: Date Calculation
1. Implement `calculate_previous_month()` function
2. Add option for custom date ranges (override previous month)
3. Add validation for date formats

### Phase 3: Data Fetching Functions
1. Implement `fetch_players_data()` - wrapper for `lib.player.all()`
2. Implement `fetch_teams_data()` - wrapper for `lib.team.all()`
3. Implement `fetch_player_career_stats_data()` - fetches career stats for all players
4. Implement `fetch_games_data()` - iterates through each day using `find_games_by_date()`
5. Implement `fetch_player_boxscores_data()` - fetches player stats for all games
6. Implement `fetch_team_boxscores_data()` - fetches team stats for all games

### Phase 4: Error Handling & Robustness
1. Add try-except blocks for API failures
2. Implement retry logic with exponential backoff
3. Add progress indicators (e.g., "Fetching games: 15/30 teams")
4. Create summary report at end

### Phase 5: CLI Integration
1. Add new subcommand to `lib/cli.py`: `seed-data`
2. Wire up to call the new script
3. Update README with usage examples

### Phase 6: Testing
1. Create `tests/scripts/test_generate_seed_data.py`
2. Test date calculation with various scenarios
3. Mock API calls to test data aggregation logic
4. Test CSV output validation

## Usage Examples

### Basic Usage (Previous Month)
```bash
# Generate seed data for previous month
python scripts/generate_seed_data.py

# Output:
# Fetching players data...
# ✓ Wrote 4,800 players to data/seed/players.csv
# 
# Fetching teams data...
# ✓ Wrote 30 teams to data/seed/teams.csv
# 
# Fetching player career stats...
# Fetching career stats: 100/4800 players
# Fetching career stats: 200/4800 players
# ...
# ✓ Wrote 45,000 career stat records to data/seed/player_career_stats.csv
# 
# Fetching games data (2024-11-01 to 2024-11-30)...
# Fetching games for 2024-11-01...
# Fetching games for 2024-11-02...
# ...
# ✓ Wrote 450 games to data/seed/games.csv
# 
# Fetching player boxscores for 450 games...
# Fetching player boxscores: 100/450 games
# Fetching player boxscores: 200/450 games
# ...
# ✓ Wrote 6,750 player boxscores to data/seed/player_boxscores.csv
# 
# Fetching team boxscores for 450 games...
# Fetching team boxscores: 100/450 games
# Fetching team boxscores: 200/450 games
# ...
# ✓ Wrote 900 team boxscores to data/seed/team_boxscores.csv
# 
# Seed data generation complete!
```

### Custom Date Range
```bash
# Generate seed data for specific date range
python scripts/generate_seed_data.py --date-from 2024-01-01 --date-to 2024-01-31
```

### Custom Output Directory
```bash
# Specify output directory
python scripts/generate_seed_data.py --output-dir custom/path
```

### Via CLI
```bash
# Using unified CLI interface
python main.py seed-data --output-dir data/seed
```

## API Rate Limiting Considerations

The NBA API has rate limiting. Best practices:

1. **Sleep between requests:** Add 0.5-second delay between API calls (based on existing patterns in `lib/game/boxscores.py` where `time.sleep(0.5)` is used)
2. **Batch operations:** Process in chunks with longer delays between batches
3. **Exponential backoff:** Retry failed requests with increasing delays
4. **Progress indicators:** Show user that script is working (not frozen)

**Note:** The 0.5-second delay is used consistently in the existing codebase (e.g., `lib/game/boxscores.py:418`) and has proven effective for avoiding rate limit issues while keeping execution time reasonable.

Example implementation:
```python
import time

def fetch_with_rate_limit(fetch_func, items, delay=0.5):
    """Fetch data with rate limiting."""
    results = []
    total = len(items)
    
    for i, item in enumerate(items, 1):
        result = fetch_func(item)
        results.append(result)
        
        # Progress indicator
        if i % 10 == 0 or i == total:
            print(f"Progress: {i}/{total} items processed")
        
        # Rate limiting
        if i < total:
            time.sleep(delay)
    
    return results
```

## Error Handling Strategy

Handle common failure scenarios gracefully:

### 1. API Timeout
```python
try:
    result = api_call()
except RequestException as e:
    print(f"API request failed: {e}")
    print("Retrying in 5 seconds...")
    time.sleep(5)
    result = api_call()  # Retry once
```

### 2. Empty Results
```python
if df.empty:
    print("Warning: No games found for this date range")
    return pd.DataFrame()
```

### 3. Partial Success
```python
# Continue processing even if some items fail
failed_items = []
for i, item in enumerate(items, 1):
    try:
        result = fetch_data(item)
        print(f"Progress: {i}/{len(items)} - Processing {item.name} (ID: {item.id})")
    except Exception as e:
        print(f"Failed to fetch data for {item.name} (ID: {item.id}): {e}")
        failed_items.append(item)
        continue

if failed_items:
    print(f"\nWarning: Failed to fetch data for {len(failed_items)} items")
    print(f"Failed items: {', '.join([f'{item.name} ({item.id})' for item in failed_items])}")
```

## Dependencies

All required packages are already in `requirements.txt`:
- `nba_api` - NBA data API client
- `pandas` - Data manipulation
- `python-dateutil` - Date calculations

No new dependencies needed.

## Testing Strategy

### Unit Tests
- Test `calculate_previous_month()` with various dates
- Test date validation logic
- Test CSV writing with mock data

### Integration Tests (with mocks)
- Mock `nba_api` responses
- Test full script execution flow
- Verify CSV output structure

### Manual Testing
- Run script during NBA season (expect data)
- Run script during off-season (expect empty/minimal game data)
- Verify CSV files can be imported to database

## Success Criteria

1. ✅ Script successfully fetches all players
2. ✅ Script successfully fetches all teams
3. ✅ Script successfully fetches player career stats for all players
4. ✅ Script calculates previous month date range automatically
5. ✅ Script fetches all games from the date range (using daily iteration)
6. ✅ Script fetches player boxscores for all games
7. ✅ Script fetches team boxscores for all games
8. ✅ All data written to well-formed CSV files
9. ✅ CSV files are suitable for database import
10. ✅ Script handles errors gracefully
11. ✅ Script provides clear progress feedback with counts and identifiers
12. ✅ Documentation is complete and clear

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limiting causes failures | High | Implement 0.5s delays (proven in existing code), retry logic, exponential backoff |
| Large date ranges cause timeouts | Medium | Provide progress indicators with counts/names, allow resume functionality |
| Fetching career stats for ~4800 players takes long time | High | Show progress every 100 players, use existing error handling, skip failed players |
| Off-season has no games | Low | Handle empty results gracefully with informative messages |
| Memory issues with large datasets | Medium | Process and write data in chunks if needed |
| Network failures | Medium | Implement retry logic, save progress periodically |

## Future Enhancements

1. **Resume capability:** Save progress and resume if interrupted
2. **Incremental updates:** Only fetch new games since last run
3. **Parallel processing:** Fetch data for multiple teams concurrently
4. **Data validation:** Verify CSV integrity before completion
5. **Database direct import:** Option to write directly to database instead of CSV
6. **Configuration file:** Allow persistent settings (output path, date range preferences)
7. **Scheduling integration:** Work with scheduler (docs/scheduler.md) for automated runs

## Timeline Estimate

- **Phase 1 (Core Structure):** 30 minutes
- **Phase 2 (Date Calculation):** 15 minutes  
- **Phase 3 (Data Fetching):** 2 hours (increased due to additional data types)
- **Phase 4 (Error Handling):** 45 minutes (increased for more complex scenarios)
- **Phase 5 (CLI Integration):** 15 minutes
- **Phase 6 (Testing):** 1 hour (increased for additional data types)

**Total Estimated Time:** ~5 hours

## References

- Existing player fetching: `lib/player/all.py`
- Existing team fetching: `lib/team/all.py`
- Existing player career stats: `lib/player/career_stats.py`
- Game finding utilities: `lib/game/boxscores.py`
- Data model documentation: `docs/data_model.md`
- CLI structure: `lib/cli.py`
- CSV helpers: `lib/helpers/csv_helpers.py`

---

## Approval

This plan provides a comprehensive blueprint for implementing the seed data generation script. It leverages existing functionality, follows project conventions, and addresses the expanded requirements including player career stats and team boxscores.

**Updated Requirements Addressed:**
1. ✅ Fetch games using daily iteration with `find_games_by_date()` (more efficient)
2. ✅ Include team stats per game (team boxscores)
3. ✅ Include career stats for all players
4. ✅ Use 0.5-second delays consistent with existing codebase
5. ✅ Provide detailed progress feedback with names/IDs

**Next Steps:**
1. Review and approve this plan
2. Proceed to implementation in phases
3. Test with real NBA data
4. Update documentation
