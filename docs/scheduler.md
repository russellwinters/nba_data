# NBA Data Scheduler Planning Document

This document outlines plans for fetching NBA data on a recurring basis. It covers scheduling options, rate limiting considerations, and strategies for keeping data fresh across all entities defined in the [Data Model](data_model.md).

---

## Table of Contents

- [Overview](#overview)
- [Entity Refresh Requirements](#entity-refresh-requirements)
- [Scheduling Options](#scheduling-options)
  - [Option 1: GitHub Actions (Recommended for Getting Started)](#option-1-github-actions-recommended-for-getting-started)
  - [Option 2: Cron Jobs](#option-2-cron-jobs)
  - [Option 3: Apache Airflow](#option-3-apache-airflow)
  - [Comparison Summary](#comparison-summary)
- [Rate Limiting Considerations](#rate-limiting-considerations)
  - [NBA Stats API Rate Limits](#nba-stats-api-rate-limits)
  - [Mitigation Strategies](#mitigation-strategies)
- [Data Freshness Strategies](#data-freshness-strategies)
  - [Static Data (Players and Teams)](#static-data-players-and-teams)
  - [Game-Level Data](#game-level-data)
  - [Career and Aggregate Stats](#career-and-aggregate-stats)
- [Implementation Recommendations](#implementation-recommendations)
  - [Phase 1: Foundation](#phase-1-foundation)
  - [Phase 2: Game Data](#phase-2-game-data)
  - [Phase 3: Player Stats](#phase-3-player-stats)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Open Questions](#open-questions)

---

## Overview

The NBA Data CLI currently supports on-demand data fetching. To maintain a complete and up-to-date dataset, we need automated scheduling that balances data freshness against API rate limits. This plan focuses on:

1. **Whole league coverage**: All 30 teams and ~500+ active players
2. **Active player focus**: Prioritizing current season data
3. **Historical completeness**: Backfilling career stats and game logs as needed
4. **API sustainability**: Respecting rate limits to avoid blocks

---

## Entity Refresh Requirements

Based on the [Data Model](data_model.md), here are the entities and their refresh characteristics:

| Entity | CLI Command | Cardinality | Volatility | Refresh Frequency |
|--------|-------------|-------------|------------|-------------------|
| **Players** | `python fetch.py players` | ~5,000 total | Low (new rookies each season) | Weekly during season, daily during draft/free agency |
| **Teams** | `python fetch.py teams` | 30 | Very low (franchise changes rare) | Monthly or on-demand |
| **Player Game Logs** | `python fetch.py player-games --player-id <ID> --season <SEASON>` | ~82 per player per season | High during season | Daily during season |
| **Player Career Stats** | `python fetch.py player-stats --player-id <ID>` | ~15-20 seasons per player | Medium | Weekly during season |
| **Player Box Scores** | `python fetch.py player-boxscores --game-id <GAME_ID>` | ~24 players per game | High (new games daily) | After each game |
| **Team Game Box Scores** | `python fetch.py team-game-boxscores --team-id <ID> --date-from <DATE> --date-to <DATE>` | ~82 per team per season | High during season | Daily during season |

### Data Volume Estimates

- **Active players**: ~500 players
- **Games per day during season**: 5-15 games (10-30 teams playing)
- **Season duration**: October through June (~9 months)
- **Off-season**: July through September (~3 months with minimal updates)

---

## Scheduling Options

### Option 1: GitHub Actions (Recommended for Getting Started)

GitHub Actions provides a straightforward, infrastructure-free scheduling solution using cron expressions in workflow files.

**Pros:**
- Zero infrastructure to manage
- Built into the repository
- Free tier includes 2,000 minutes/month for private repos, unlimited for public
- Easy to trigger manually for backfills
- Native integration with repository secrets for credentials
- Automatic retry and failure notifications

**Cons:**
- Limited to 5-minute minimum cron granularity
- Workflows can be delayed during high-demand periods
- Not suitable for complex DAG dependencies
- Maximum workflow runtime of 6 hours

**Example Workflow:**

```yaml
# .github/workflows/scheduled-fetch.yml
name: Scheduled NBA Data Fetch

on:
  schedule:
    # Run daily at 6 AM UTC (after most games complete)
    - cron: '0 6 * * *'
  workflow_dispatch:  # Allow manual triggers

jobs:
  fetch-players:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python fetch.py players --output data/players.csv
      - uses: actions/upload-artifact@v4
        with:
          name: players-data
          path: data/players.csv

  fetch-team-games:
    runs-on: ubuntu-latest
    needs: fetch-players  # Ensures sequential execution to avoid rate limits
    strategy:
      matrix:
        team: [ATL, BOS, BKN, CHA, CHI, CLE, DAL, DEN, DET, GSW, 
               HOU, IND, LAC, LAL, MEM, MIA, MIL, MIN, NOP, NYK,
               OKC, ORL, PHI, PHX, POR, SAC, SAS, TOR, UTA, WAS]
      max-parallel: 2  # Limit concurrent API calls
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: |
          python fetch.py team-game-boxscores \
            --team-id ${{ matrix.team }} \
            --date-from $(date -d "yesterday" +%Y-%m-%d) \
            --date-to $(date +%Y-%m-%d)
```

### Option 2: Cron Jobs

Traditional Unix cron jobs on a dedicated server or cloud VM.

**Pros:**
- Full control over execution environment
- No external dependencies
- Minute-level granularity
- Persistent local storage

**Cons:**
- Requires server infrastructure
- Manual monitoring setup needed
- No built-in retry logic
- Single point of failure without clustering

**Example Crontab:**

```bash
# /etc/cron.d/nba-data-fetch

# Fetch players weekly on Sunday at 3 AM
0 3 * * 0 nba /home/nba/nba_data/scripts/fetch_players.sh >> /var/log/nba/players.log 2>&1

# Fetch team games daily at 6 AM (after games complete)
0 6 * * * nba /home/nba/nba_data/scripts/fetch_team_games.sh >> /var/log/nba/team_games.log 2>&1

# Fetch active player game logs daily at 7 AM (staggered to avoid rate limits)
0 7 * * * nba /home/nba/nba_data/scripts/fetch_player_games.sh >> /var/log/nba/player_games.log 2>&1
```

### Option 3: Apache Airflow

Enterprise-grade workflow orchestration for complex data pipelines.

**Pros:**
- DAG-based dependency management
- Built-in monitoring and alerting
- Backfill capabilities with date ranges
- Retry policies and SLA tracking
- Web UI for observability

**Cons:**
- Significant infrastructure overhead
- Learning curve for DAG authoring
- Overkill for simple scheduling needs
- Requires metadata database (PostgreSQL recommended)

**Example DAG:**

```python
# dags/nba_data_pipeline.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'nba_data',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@example.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'nba_daily_fetch',
    default_args=default_args,
    description='Daily NBA data fetch pipeline',
    schedule_interval='0 6 * * *',  # 6 AM UTC daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    fetch_players = BashOperator(
        task_id='fetch_players',
        bash_command='cd /opt/nba_data && python fetch.py players',
    )

    fetch_teams = BashOperator(
        task_id='fetch_teams',
        bash_command='cd /opt/nba_data && python fetch.py teams',
    )

    # Dynamic task generation for teams
    team_tasks = []
    for team in ['LAL', 'GSW', 'BOS']:  # Abbreviated for example
        task = BashOperator(
            task_id=f'fetch_team_games_{team}',
            bash_command=f'cd /opt/nba_data && python fetch.py team-game-boxscores --team-id {team} --date {{{{ ds }}}}',
            pool='nba_api_pool',  # Limit concurrent API calls
        )
        team_tasks.append(task)

    fetch_players >> fetch_teams >> team_tasks
```

### Comparison Summary

| Criterion | GitHub Actions | Cron Jobs | Apache Airflow |
|-----------|----------------|-----------|----------------|
| **Setup Complexity** | Low | Medium | High |
| **Infrastructure** | None | Server required | Cluster recommended |
| **Cost** | Free for public repos | Server costs | Server + DB costs |
| **Monitoring** | Basic (workflow logs) | Manual setup | Built-in UI |
| **Rate Limit Control** | Matrix + max-parallel | Custom scripting | Pool-based |
| **Backfill Support** | Manual dispatch | Manual scripting | Native |
| **Best For** | Small-medium projects | Self-hosted simple jobs | Enterprise pipelines |

**Recommendation**: Start with **GitHub Actions** for simplicity. Migrate to **Airflow** if you need complex dependencies, backfills, or observability at scale.

---

## Rate Limiting Considerations

### NBA Stats API Rate Limits

The NBA Stats API (stats.nba.com) is an unofficial API with undocumented rate limits. Based on community observations:

| Limit Type | Observed Threshold | Consequence |
|------------|-------------------|-------------|
| **Per-minute** | ~20-30 requests | Temporary 403 or 429 responses |
| **Per-hour** | ~200-300 requests | Extended blocking (minutes to hours) |
| **Per-day** | ~1,000-2,000 requests | Potential IP-based blocking |
| **Burst** | >5 requests in <1 second | Immediate rejection |

**Note**: These limits are approximate and may change without notice. The API may also block requests missing proper headers (User-Agent, Referer).

### Mitigation Strategies

#### 1. Request Throttling

Implement delays between API calls to stay under rate limits.

```python
# lib/helpers/rate_limiter.py
import time
from functools import wraps

def rate_limit(min_interval_seconds=2.0):
    """Decorator to enforce minimum interval between API calls."""
    last_call_time = [0]  # Mutable container for closure
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call_time[0]
            if elapsed < min_interval_seconds:
                time.sleep(min_interval_seconds - elapsed)
            result = func(*args, **kwargs)
            last_call_time[0] = time.time()
            return result
        return wrapper
    return decorator
```

#### 2. Batch Processing with Delays

Group requests with sleep intervals between batches.

```python
def fetch_all_active_player_stats(player_ids, batch_size=10, delay_between_batches=60):
    """Fetch career stats for all active players with rate limiting."""
    results = []
    for i in range(0, len(player_ids), batch_size):
        batch = player_ids[i:i + batch_size]
        for player_id in batch:
            result = fetch_player_stats(player_id)
            results.append(result)
            time.sleep(2)  # 2 seconds between individual requests
        
        if i + batch_size < len(player_ids):
            print(f"Completed batch {i // batch_size + 1}, sleeping {delay_between_batches}s...")
            time.sleep(delay_between_batches)
    
    return results
```

#### 3. Incremental Fetching

Only fetch new or changed data instead of full refreshes.

```python
def fetch_new_games_only(team_id, last_fetch_date):
    """Fetch only games that occurred after the last fetch."""
    today = datetime.now().strftime('%Y-%m-%d')
    return fetch_team_games(
        team_id=team_id,
        date_from=last_fetch_date,
        date_to=today
    )
```

#### 4. Request Prioritization

Prioritize frequently-changing data over static data.

| Priority | Entity | Rationale |
|----------|--------|-----------|
| High | Team Game Box Scores | New games every day |
| High | Player Box Scores | Needed for game-level analysis |
| Medium | Player Game Logs | Can lag by a day |
| Low | Player Career Stats | Only changes after games |
| Lowest | Players, Teams | Rarely changes |

#### 5. Proper Headers

Ensure requests include appropriate headers to avoid blocks.

```python
# nba_api already handles this, but verify configuration
from nba_api.stats.static import players
from nba_api.stats.library.parameters import PerModeSimple
```

#### 6. Retry with Exponential Backoff

Handle transient failures gracefully.

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=5):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
```

---

## Data Freshness Strategies

### Static Data (Players and Teams)

**Entities**: `players`, `teams`

**Characteristics**:
- Rarely changes (new players during draft/trades, team relocations extremely rare)
- Full refresh is low-cost (30 teams, ~5,000 players from one API call each)

**Strategy**:
| Period | Frequency | Rationale |
|--------|-----------|-----------|
| Regular Season | Weekly (Sunday 3 AM) | Catch late signings, trades |
| Off-Season (July-Sept) | Daily (during draft week), Weekly otherwise | Draft picks, free agency |
| Trade Deadline (Feb) | Daily for 1 week | Trades finalize |

**Implementation**:
```bash
# Weekly player refresh
python fetch.py players --output data/players.csv

# Compare with previous to detect changes
diff data/players.csv data/players_prev.csv
```

### Game-Level Data

**Entities**: `player_game_logs`, `player_box_scores`, `team_game_box_scores`

**Characteristics**:
- Changes frequently during season (5-15 games per day)
- Game data is immutable once final (except rare stat corrections)
- Need to capture all games without gaps

**Strategy**:
| Period | Frequency | Approach |
|--------|-----------|----------|
| Regular Season | Daily at 6 AM UTC | Incremental fetch for yesterday's games |
| Playoffs | Daily at 6 AM UTC | Same as regular season |
| Off-Season | None | No games to fetch |

**Implementation for Incremental Daily Fetch**:
```python
def daily_game_fetch():
    """Fetch all games from yesterday."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    teams = get_all_team_abbreviations()  # ['ATL', 'BOS', ...]
    
    for team in teams:
        # Fetch team's games from yesterday
        df = fetch_team_games(
            team_id=team,
            date_from=yesterday,
            date_to=yesterday
        )
        
        if not df.empty:
            # Save to partitioned storage
            save_to_storage(df, partition_date=yesterday, team=team)
            
            # Fetch player box scores for each game
            for game_id in df['GAME_ID'].unique():
                fetch_player_boxscores_by_game(game_id)
        
        time.sleep(3)  # Rate limiting
```

**Optimization: Game Discovery First**

Instead of querying each team, use a league-wide scoreboard endpoint to discover which games happened:

```python
from nba_api.stats.endpoints import scoreboardv2

def get_yesterdays_game_ids():
    """Get all game IDs from yesterday."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    scoreboard = scoreboardv2.ScoreboardV2(game_date=yesterday)
    games_df = scoreboard.get_data_frames()[0]
    return games_df['GAME_ID'].tolist()
```

### Career and Aggregate Stats

**Entities**: `player_career_stats`

**Characteristics**:
- Changes after each game a player plays
- Only active players need regular updates
- Historical players' stats are static

**Strategy**:
| Player Type | Frequency | Rationale |
|-------------|-----------|-----------|
| Active Players (~500) | Weekly during season | Aggregate stats change slowly |
| Historical Players | On-demand only | Stats are immutable |

**Implementation**:
```python
def weekly_career_stats_update():
    """Update career stats for all active players."""
    # Get active player IDs
    players_df = pd.read_csv('data/players.csv')
    active_ids = players_df[players_df['is_active']]['id'].tolist()
    
    # Fetch in batches with rate limiting
    for i, player_id in enumerate(active_ids):
        fetch_player_stats(player_id, output_path=f'data/career/{player_id}.csv')
        
        if (i + 1) % 10 == 0:
            print(f"Fetched {i + 1}/{len(active_ids)} players")
            time.sleep(60)  # Pause every 10 players
        else:
            time.sleep(3)  # Brief pause between requests
```

---

## Implementation Recommendations

### Phase 1: Foundation

**Duration**: 1-2 weeks

**Goals**:
1. Implement rate limiting utilities in `lib/helpers/`
2. Set up GitHub Actions workflow for players and teams
3. Create simple logging/tracking for fetch status

**Tasks**:
- [ ] Create `lib/helpers/rate_limiter.py` with throttling decorator
- [ ] Create `lib/helpers/fetch_tracker.py` to record last fetch timestamps
- [ ] Create `.github/workflows/scheduled-fetch-foundation.yml` for players/teams
- [ ] Test workflow with manual dispatch
- [ ] Set up artifact storage for fetched data

### Phase 2: Game Data

**Duration**: 2-3 weeks

**Goals**:
1. Implement daily game discovery and fetching
2. Create incremental fetch logic (avoid re-fetching old games)
3. Set up partitioned storage structure

**Tasks**:
- [ ] Create `lib/helpers/game_discovery.py` using ScoreboardV2
- [ ] Modify `fetch_team_box_scores.py` to support incremental mode
- [ ] Create `.github/workflows/scheduled-fetch-games.yml`
- [ ] Implement data partitioning (by date or game_id)
- [ ] Add duplicate detection to prevent re-fetching

### Phase 3: Player Stats

**Duration**: 2-3 weeks

**Goals**:
1. Implement batch player stats fetching with proper rate limiting
2. Create prioritized fetch queue (active players first)
3. Implement backfill capability for historical data

**Tasks**:
- [ ] Create `lib/batch_fetch.py` with chunked processing
- [ ] Implement player prioritization (active > historical)
- [ ] Create `.github/workflows/scheduled-fetch-player-stats.yml`
- [ ] Add progress tracking and resumability for long-running fetches
- [ ] Create backfill workflow with date range parameters

---

## Monitoring and Alerting

### Key Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Fetch Success Rate | % of successful API calls | < 95% |
| Data Freshness | Time since last successful fetch | > 24 hours |
| API Errors | Count of 403/429/5xx responses | > 10 per run |
| Missing Games | Games in scoreboard but not in data | Any |
| Run Duration | Time to complete scheduled fetch | > 4 hours |

### GitHub Actions Alerting

Use workflow status and GitHub notifications for basic alerting:

```yaml
jobs:
  fetch-data:
    runs-on: ubuntu-latest
    steps:
      # ... fetch steps ...
      
      - name: Notify on Failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Scheduled fetch failed on ${new Date().toISOString().split('T')[0]}`,
              body: `Workflow run failed: ${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`,
              labels: ['automation', 'bug']
            })
```

### Logging Strategy

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/fetch_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('nba_data')
```

---

## Open Questions

The following questions require input before finalizing the implementation:

1. **Data Storage Destination**: Where should fetched data be stored long-term?
   - Local CSV files (current approach)
   - SQLite database
   - Cloud storage (S3, GCS)
   - Data warehouse (BigQuery, Snowflake)

2. **Historical Backfill Scope**: How far back should we backfill historical data?
   - Current season only
   - Last N seasons
   - All available history (~1996-present)

3. **Player Game Logs Priority**: Should we fetch game logs for all players or prioritize?
   - All active players
   - Players who played yesterday
   - Top N players by minutes/games

4. **Failure Recovery**: How should we handle partial failures?
   - Retry entire batch
   - Skip and continue
   - Manual intervention required

5. **Data Validation**: What validation should be performed on fetched data?
   - Schema validation
   - Completeness checks (all games present)
   - Anomaly detection (unusual stat values)

6. **Cost Constraints**: Are there budget limitations for infrastructure?
   - GitHub Actions minutes
   - Cloud compute costs
   - Storage costs

---

## Related Documentation

- [Data Model](data_model.md) - Entity schemas and relationships
- [README](../README.md) - CLI usage and project overview
- [nba_api Documentation](https://github.com/swar/nba_api) - Underlying API library

---

## Revision History

| Date | Author | Description |
|------|--------|-------------|
| 2024-11-28 | Copilot | Initial planning document |
