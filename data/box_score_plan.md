# Box Score API Investigation - Action Plan

## Objective

Investigate the `nba_api` library to find all APIs that provide access to game data based on:
- Team ID and a given date
- Team ID or Game ID
- Data that enables retrieval of box scores for each team involved

This document outlines alternatives to `TeamGameLog` and `TeamGameLogs` endpoints.

---

## Summary of Findings

### Primary Box Score Endpoints (Require Game ID)

These endpoints require a `game_id` and return detailed box score data for both teams:

| Endpoint | Description | Key Data |
|----------|-------------|----------|
| **BoxScoreTraditionalV2/V3** | Traditional box score stats | Points, rebounds, assists, FG%, etc. per player/team |
| **BoxScoreAdvancedV2/V3** | Advanced analytics | Off/Def rating, eFG%, TS%, pace, PIE, etc. |
| **BoxScoreSummaryV2** | Game summary with metadata | Final scores, game info, officials, line scores |
| **BoxScoreScoringV2/V3** | Detailed scoring breakdown | 2pt/3pt percentages, points in paint, fastbreak pts |
| **BoxScoreMiscV2/V3** | Miscellaneous stats | Points off turnovers, second chance points |
| **BoxScoreHustleV2** | Hustle stats | Deflections, loose balls, contested shots |
| **BoxScorePlayerTrackV2/V3** | Player tracking data | Speed, distance traveled, touches |
| **BoxScoreUsageV2/V3** | Usage statistics | Usage rate, percentage of plays |
| **BoxScoreMatchupsV3** | Player matchups | Head-to-head defensive matchups |
| **HustleStatsBoxScore** | Hustle metrics | Contested shots, deflections, charges drawn |

### Game Discovery Endpoints (Find Game IDs)

These endpoints help find games by team, date, or other criteria:

| Endpoint | Description | How to Use |
|----------|-------------|------------|
| **LeagueGameFinder** | Most flexible search | Supports `team_id_nullable`, `date_from_nullable`, `date_to_nullable`, `season_nullable` |
| **TeamGameLog** | Team game log | Requires `team_id`, optional `season`, returns `GAME_ID` for each game |
| **TeamGameLogs** | Enhanced team game log | More filters including `date_from_nullable`, `date_to_nullable`, `opp_team_id_nullable` |
| **ScoreboardV2** | Daily scoreboard | By date - returns all games on a given day with `GAME_ID` |
| **ScheduleLeagueV2** | Full season schedule | Returns all scheduled/completed games with `gameId` |
| **LeagueGameLog** | League-wide game log | All team games for a season |
| **CumeStatsTeamGames** | Cumulative team games | Returns `GAME_ID` and matchup info |

---

## Recommended Workflow for Getting Box Scores

### Strategy 1: By Team ID and Date Range

```python
from nba_api.stats.endpoints import leaguegamefinder

# Find games for a specific team in a date range
games = leaguegamefinder.LeagueGameFinder(
    team_id_nullable=1610612747,  # Lakers
    date_from_nullable='01/01/2024',
    date_to_nullable='01/31/2024'
)
game_ids = games.get_data_frames()[0]['GAME_ID'].tolist()
```

### Strategy 2: By Date (All Games)

```python
from nba_api.stats.endpoints import scoreboardv2

# Get all games on a specific date
scoreboard = scoreboardv2.ScoreboardV2(game_date='2024-01-15')
game_headers = scoreboard.get_data_frames()[0]  # GameHeader
game_ids = game_headers['GAME_ID'].tolist()
```

### Strategy 3: Retrieve Box Score Using Game ID

```python
from nba_api.stats.endpoints import (
    boxscoretraditionalv3,
    boxscoresummaryv2,
    boxscoreadvancedv3
)

game_id = '0022400123'

# Traditional box score
traditional = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
player_stats = traditional.player_stats.get_data_frame()
team_stats = traditional.team_stats.get_data_frame()

# Game summary (line scores, officials, etc.)
summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
line_score = summary.line_score.get_data_frame()

# Advanced stats
advanced = boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game_id)
player_advanced = advanced.player_stats.get_data_frame()
```

---

## API Details

### LeagueGameFinder

**Best for:** Finding games by team, date range, or other criteria

**Key Parameters:**
- `team_id_nullable`: Filter by team ID
- `date_from_nullable`: Start date (MM/DD/YYYY format)
- `date_to_nullable`: End date (MM/DD/YYYY format)
- `season_nullable`: Filter by season (e.g., '2023-24')
- `player_or_team_abbreviation`: 'T' for teams, 'P' for players
- `game_id_nullable`: Find a specific game
- `vs_team_id_nullable`: Find games against a specific opponent

**Returns:**
- `GAME_ID`, `GAME_DATE`, `MATCHUP`, `WL`, `PTS`, `FGM`, `FGA`, `FG_PCT`, `FG3M`, `FG3A`, `FG3_PCT`, `FTM`, `FTA`, `FT_PCT`, `REB`, `AST`, `STL`, `BLK`, `TOV`, `PF`, `PLUS_MINUS`

---

### ScoreboardV2

**Best for:** Getting all games on a specific date

**Key Parameters:**
- `game_date`: Date in YYYY-MM-DD format
- `day_offset`: Offset from the date (0 for same day)
- `league_id`: '00' for NBA

**Returns (Multiple DataFrames):**
- `GameHeader`: Game ID, status, home/visitor team IDs, arena info
- `LineScore`: Quarter-by-quarter scores for each team
- `TeamLeaders`: Top scorers/rebounders/assists leaders per team
- `LastMeeting`: Previous matchup info
- `EastConfStandingsByDay`/`WestConfStandingsByDay`: Standings

---

### BoxScoreTraditionalV2/V3

**Best for:** Standard box score statistics

**Key Parameters:**
- `game_id`: Required - the game identifier

**Returns:**
- `PlayerStats`: Per-player stats (minutes, points, rebounds, assists, etc.)
- `TeamStats`: Team aggregate stats
- `StarterBenchStats` (V2 only): Starter vs bench splits

---

### BoxScoreSummaryV2

**Best for:** Game metadata and summary

**Key Parameters:**
- `game_id`: Required - the game identifier

**Returns:**
- `GameSummary`: Basic game info, attendance, game time
- `LineScore`: Quarter-by-quarter scores
- `SeasonSeries`: Season series record between teams
- `Officials`: Referee assignments
- `GameInfo`: Additional game details

---

### BoxScoreAdvancedV2/V3

**Best for:** Advanced analytics

**Key Parameters:**
- `game_id`: Required - the game identifier
- `start_period` / `end_period`: Optional period filters

**Returns:**
- `PlayerStats`: Off/Def rating, eFG%, TS%, AST_PCT, etc.
- `TeamStats`: Team-level advanced metrics

---

## Complete Endpoint Reference

### Box Score Endpoints (Require Game ID)

| Endpoint | V2 | V3 | Purpose |
|----------|----|----|---------|
| BoxScoreTraditional | ✓ | ✓ | Standard stats |
| BoxScoreAdvanced | ✓ | ✓ | Advanced metrics |
| BoxScoreSummary | ✓ | - | Game summary |
| BoxScoreScoring | ✓ | ✓ | Scoring breakdown |
| BoxScoreMisc | ✓ | ✓ | Miscellaneous stats |
| BoxScoreHustle | ✓ | - | Hustle metrics |
| BoxScorePlayerTrack | ✓ | ✓ | Player tracking |
| BoxScoreUsage | ✓ | ✓ | Usage statistics |
| BoxScoreMatchups | - | ✓ | Player matchups |
| BoxScoreFourFactors | ✓ | ✓ | Four factors analysis |
| BoxScoreDefensive | ✓ | - | Defensive stats |

### Game Discovery Endpoints

| Endpoint | By Team | By Date | By Season | Returns Game ID |
|----------|---------|---------|-----------|-----------------|
| LeagueGameFinder | ✓ | ✓ | ✓ | ✓ |
| TeamGameLog | ✓ | ✓ | ✓ | ✓ |
| TeamGameLogs | ✓ | ✓ | ✓ | ✓ |
| ScoreboardV2 | - | ✓ | - | ✓ |
| ScheduleLeagueV2 | - | - | ✓ | ✓ |
| LeagueGameLog | - | - | ✓ | ✓ |

---

## Recommendations

### For Finding Games by Team and Date:
1. **Primary:** Use `LeagueGameFinder` - most flexible with team, date, and opponent filters
2. **Alternative:** Use `TeamGameLogs` with `date_from_nullable` and `date_to_nullable`

### For Finding Games by Date Only:
1. **Primary:** Use `ScoreboardV2` - gives all games on a specific date
2. **Alternative:** Use `LeagueGameFinder` with date filters

### For Getting Box Scores:
1. **Traditional Stats:** `BoxScoreTraditionalV3` (or V2)
2. **Advanced Metrics:** `BoxScoreAdvancedV3` (or V2)
3. **Complete Summary:** `BoxScoreSummaryV2`
4. **All Data:** Combine multiple box score endpoints

---

## Implementation Notes

### Game ID Format
- NBA game IDs are 10-character strings (e.g., `0022400123`)
- Format: `XYYZZZNNNN` where:
  - `X`: Game type (0 = regular, 4 = playoffs)
  - `YY`: Season type (02 = regular season, 04 = playoffs)
  - `ZZZ`: Season year (last 3 digits, e.g., 240 for 2024)
  - `NNNN`: Game number

### Rate Limiting
- NBA API has rate limits; implement delays between requests
- Recommended: 0.5-1 second delay between API calls

### Error Handling
- Some games may not have all data available (especially for older games)
- V3 endpoints may not have data for games before ~2020

---

## POC Implementation

See `/lib/demo_boxscores.py` for a proof-of-concept implementation demonstrating:
1. Finding games using `LeagueGameFinder`
2. Finding games by date using `ScoreboardV2`
3. Retrieving box scores using `BoxScoreTraditionalV3`
4. Retrieving game summaries using `BoxScoreSummaryV2`
