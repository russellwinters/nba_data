# NBA Data Model Documentation

This document describes the data structures returned by the NBA Data CLI commands, modeled as SQL database tables. Each entity represents the structure of the CSV output from the corresponding CLI command.

## Table of Contents

- [Overview](#overview)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Tables](#tables)
  - [Players](#players)
  - [Teams](#teams)
  - [Player Game Logs](#player-game-logs)
  - [Player Career Stats](#player-career-stats)
  - [Player Box Scores](#player-box-scores)
  - [Team Game Box Scores](#team-game-box-scores)

---

## Overview

The NBA Data CLI fetches data from the NBA Stats API and outputs CSV files. This document models those CSV outputs as relational database tables, providing:

- **Column definitions** with SQL data types
- **Primary and foreign key relationships**
- **Column descriptions** explaining each field
- **Sample CLI commands** to generate the data

---

## Entity Relationship Diagram

```
                    ┌─────────────────┐
                    │     Players     │
                    ├─────────────────┤
                    │ PK: id          │
                    │ full_name       │
                    │ first_name      │
                    │ last_name       │
                    │ is_active       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Player Game     │ │ Player Career   │ │ Player Box      │
│ Logs            │ │ Stats           │ │ Scores          │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ FK: Player_ID   │ │ FK: PLAYER_ID   │ │ FK: PLAYER_ID   │
│ Game_ID         │ │ SEASON_ID       │ │ FK: TEAM_ID ────┼──┐
│ SEASON_ID       │ │ FK: TEAM_ID ────┼─┼─┐ GAME_ID       │  │
│ GAME_DATE       │ │ Stats...        │ │ │ Stats...      │  │
│ Stats...        │ │                 │ │ │               │  │
└─────────────────┘ └─────────────────┘ │ └───────────────┘  │
                                        │                    │
                    ┌─────────────────┐ │                    │
                    │     Teams       │ │                    │
                    ├─────────────────┤ │                    │
                    │ PK: id     ◄────┼─┴────────────────────┘
                    │ full_name       │
                    │ abbreviation    │
                    │ nickname        │
                    │ city, state     │
                    │ year_founded    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Team Game Box   │
                    │ Scores          │
                    ├─────────────────┤
                    │ FK: TEAM_ID     │
                    │ GAME_ID         │
                    │ GAME_DATE       │
                    │ MATCHUP         │
                    │ Stats...        │
                    └─────────────────┘
```

**Key relationships:**
- **Players → Player Game Logs**: One player has many game logs (one per game played)
- **Players → Player Career Stats**: One player has many career stat records (one per season/team)
- **Players → Player Box Scores**: One player has many box scores (one per game)
- **Teams → Player Career Stats**: One team appears in many player career records
- **Teams → Player Box Scores**: One team appears in many player box scores
- **Teams → Team Game Box Scores**: One team has many game box scores

---

## Tables

### Players

**CLI Command:** `python fetch.py players --output data/players.csv`

**Description:** Contains all NBA players (historical and current) with basic identifying information.

#### Schema

| Column      | SQL Type     | Nullable | Description                                      |
|-------------|--------------|----------|--------------------------------------------------|
| `id`        | INTEGER      | NOT NULL | **Primary Key.** Unique NBA player identifier    |
| `full_name` | VARCHAR(100) | NOT NULL | Player's full display name                       |
| `first_name`| VARCHAR(50)  | NOT NULL | Player's first name                              |
| `last_name` | VARCHAR(50)  | NOT NULL | Player's last name                               |
| `is_active` | BOOLEAN      | NOT NULL | Whether the player is currently active in the NBA|

#### SQL DDL

```sql
CREATE TABLE players (
    id          INTEGER      PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  NOT NULL,
    is_active   BOOLEAN      NOT NULL
);

CREATE INDEX idx_players_full_name ON players(full_name);
CREATE INDEX idx_players_is_active ON players(is_active);
```

#### Sample Data

| id    | full_name           | first_name | last_name    | is_active |
|-------|---------------------|------------|--------------|-----------|
| 2544  | LeBron James        | LeBron     | James        | True      |
| 201939| Stephen Curry       | Stephen    | Curry        | True      |
| 76003 | Kareem Abdul-Jabbar | Kareem     | Abdul-Jabbar | False     |

---

### Teams

**CLI Command:** `python fetch.py teams --output data/teams.csv`

**Description:** Contains all 30 current NBA franchises with location and founding information.

#### Schema

| Column        | SQL Type     | Nullable | Description                                        |
|---------------|--------------|----------|----------------------------------------------------|
| `id`          | INTEGER      | NOT NULL | **Primary Key.** Unique NBA team identifier        |
| `full_name`   | VARCHAR(50)  | NOT NULL | Full team name (e.g., "Los Angeles Lakers")        |
| `abbreviation`| CHAR(3)      | NOT NULL | Three-letter team abbreviation (e.g., "LAL")       |
| `nickname`    | VARCHAR(30)  | NOT NULL | Team nickname (e.g., "Lakers")                     |
| `city`        | VARCHAR(30)  | NOT NULL | Team's home city                                   |
| `state`       | VARCHAR(30)  | NOT NULL | Team's home state/province                         |
| `year_founded`| INTEGER      | NOT NULL | Year the franchise was established                 |

#### SQL DDL

```sql
CREATE TABLE teams (
    id            INTEGER     PRIMARY KEY,
    full_name     VARCHAR(50) NOT NULL,
    abbreviation  CHAR(3)     NOT NULL UNIQUE,
    nickname      VARCHAR(30) NOT NULL,
    city          VARCHAR(30) NOT NULL,
    state         VARCHAR(30) NOT NULL,
    year_founded  INTEGER     NOT NULL
);

CREATE INDEX idx_teams_abbreviation ON teams(abbreviation);
CREATE INDEX idx_teams_city ON teams(city);
```

#### Sample Data

| id         | full_name          | abbreviation | nickname | city        | state      | year_founded |
|------------|--------------------|--------------|----------|-------------|------------|--------------|
| 1610612747 | Los Angeles Lakers | LAL          | Lakers   | Los Angeles | California | 1948         |
| 1610612738 | Boston Celtics     | BOS          | Celtics  | Boston      | Massachusetts | 1946       |
| 1610612744 | Golden State Warriors | GSW       | Warriors | San Francisco | California | 1946       |

---

### Player Game Logs

**CLI Command:** `python fetch.py player-games --player-id <ID> --season <SEASON>`

**Description:** Contains per-game statistics for a specific player during a given season. Each row represents one game played by the player.

#### Schema

| Column          | SQL Type       | Nullable | Description                                          |
|-----------------|----------------|----------|------------------------------------------------------|
| `SEASON_ID`     | VARCHAR(10)    | NOT NULL | Season identifier (e.g., "22022" for 2022-23)        |
| `Player_ID`     | INTEGER        | NOT NULL | **Foreign Key** to `players.id`                      |
| `Game_ID`       | VARCHAR(10)    | NOT NULL | Unique game identifier                               |
| `GAME_DATE`     | DATE           | NOT NULL | Date the game was played                             |
| `MATCHUP`       | VARCHAR(20)    | NOT NULL | Game matchup (e.g., "LAL vs. GSW" or "LAL @ BOS")    |
| `WL`            | CHAR(1)        | NULL     | Win/Loss indicator ("W" or "L")                      |
| `MIN`           | INTEGER        | NULL     | Minutes played                                       |
| `FGM`           | INTEGER        | NULL     | Field goals made                                     |
| `FGA`           | INTEGER        | NULL     | Field goals attempted                                |
| `FG_PCT`        | DECIMAL(5,3)   | NULL     | Field goal percentage                                |
| `FG3M`          | INTEGER        | NULL     | Three-point field goals made                         |
| `FG3A`          | INTEGER        | NULL     | Three-point field goals attempted                    |
| `FG3_PCT`       | DECIMAL(5,3)   | NULL     | Three-point field goal percentage                    |
| `FTM`           | INTEGER        | NULL     | Free throws made                                     |
| `FTA`           | INTEGER        | NULL     | Free throws attempted                                |
| `FT_PCT`        | DECIMAL(5,3)   | NULL     | Free throw percentage                                |
| `OREB`          | INTEGER        | NULL     | Offensive rebounds                                   |
| `DREB`          | INTEGER        | NULL     | Defensive rebounds                                   |
| `REB`           | INTEGER        | NULL     | Total rebounds                                       |
| `AST`           | INTEGER        | NULL     | Assists                                              |
| `STL`           | INTEGER        | NULL     | Steals                                               |
| `BLK`           | INTEGER        | NULL     | Blocks                                               |
| `TOV`           | INTEGER        | NULL     | Turnovers                                            |
| `PF`            | INTEGER        | NULL     | Personal fouls                                       |
| `PTS`           | INTEGER        | NULL     | Points scored                                        |
| `PLUS_MINUS`    | INTEGER        | NULL     | Plus/minus rating for the game                       |
| `VIDEO_AVAILABLE`| INTEGER       | NULL     | Video availability flag (0 or 1)                     |

#### SQL DDL

```sql
CREATE TABLE player_game_logs (
    SEASON_ID       VARCHAR(10)   NOT NULL,
    Player_ID       INTEGER       NOT NULL,
    Game_ID         VARCHAR(10)   NOT NULL,
    GAME_DATE       DATE          NOT NULL,
    MATCHUP         VARCHAR(20)   NOT NULL,
    WL              CHAR(1),
    MIN             INTEGER,
    FGM             INTEGER,
    FGA             INTEGER,
    FG_PCT          DECIMAL(5,3),
    FG3M            INTEGER,
    FG3A            INTEGER,
    FG3_PCT         DECIMAL(5,3),
    FTM             INTEGER,
    FTA             INTEGER,
    FT_PCT          DECIMAL(5,3),
    OREB            INTEGER,
    DREB            INTEGER,
    REB             INTEGER,
    AST             INTEGER,
    STL             INTEGER,
    BLK             INTEGER,
    TOV             INTEGER,
    PF              INTEGER,
    PTS             INTEGER,
    PLUS_MINUS      INTEGER,
    VIDEO_AVAILABLE INTEGER,
    PRIMARY KEY (Player_ID, Game_ID),
    FOREIGN KEY (Player_ID) REFERENCES players(id)
);

CREATE INDEX idx_player_game_logs_season ON player_game_logs(SEASON_ID);
CREATE INDEX idx_player_game_logs_date ON player_game_logs(GAME_DATE);
CREATE INDEX idx_player_game_logs_player ON player_game_logs(Player_ID);
```

---

### Player Career Stats

**CLI Command:** `python fetch.py player-stats --player-id <ID>`

**Description:** Contains season-by-season career statistics for a specific player. The primary result set is `SeasonTotalsRegularSeason`, which provides regular season statistics broken down by season and team.

#### Schema

| Column            | SQL Type       | Nullable | Description                                          |
|-------------------|----------------|----------|------------------------------------------------------|
| `PLAYER_ID`       | INTEGER        | NOT NULL | **Foreign Key** to `players.id`                      |
| `SEASON_ID`       | VARCHAR(10)    | NOT NULL | Season identifier (e.g., "2022-23")                  |
| `LEAGUE_ID`       | VARCHAR(5)     | NOT NULL | League identifier (e.g., "00" for NBA)               |
| `TEAM_ID`         | INTEGER        | NOT NULL | **Foreign Key** to `teams.id`                        |
| `TEAM_ABBREVIATION`| CHAR(3)       | NOT NULL | Three-letter team abbreviation                       |
| `PLAYER_AGE`      | INTEGER        | NULL     | Player's age during the season                       |
| `GP`              | INTEGER        | NULL     | Games played                                         |
| `GS`              | INTEGER        | NULL     | Games started                                        |
| `MIN`             | DECIMAL(10,1)  | NULL     | Total minutes played                                 |
| `FGM`             | INTEGER        | NULL     | Field goals made                                     |
| `FGA`             | INTEGER        | NULL     | Field goals attempted                                |
| `FG_PCT`          | DECIMAL(5,3)   | NULL     | Field goal percentage                                |
| `FG3M`            | INTEGER        | NULL     | Three-point field goals made                         |
| `FG3A`            | INTEGER        | NULL     | Three-point field goals attempted                    |
| `FG3_PCT`         | DECIMAL(5,3)   | NULL     | Three-point field goal percentage                    |
| `FTM`             | INTEGER        | NULL     | Free throws made                                     |
| `FTA`             | INTEGER        | NULL     | Free throws attempted                                |
| `FT_PCT`          | DECIMAL(5,3)   | NULL     | Free throw percentage                                |
| `OREB`            | INTEGER        | NULL     | Offensive rebounds                                   |
| `DREB`            | INTEGER        | NULL     | Defensive rebounds                                   |
| `REB`             | INTEGER        | NULL     | Total rebounds                                       |
| `AST`             | INTEGER        | NULL     | Assists                                              |
| `STL`             | INTEGER        | NULL     | Steals                                               |
| `BLK`             | INTEGER        | NULL     | Blocks                                               |
| `TOV`             | INTEGER        | NULL     | Turnovers                                            |
| `PF`              | INTEGER        | NULL     | Personal fouls                                       |
| `PTS`             | INTEGER        | NULL     | Points scored                                        |

#### SQL DDL

```sql
CREATE TABLE player_career_stats (
    PLAYER_ID         INTEGER       NOT NULL,
    SEASON_ID         VARCHAR(10)   NOT NULL,
    LEAGUE_ID         VARCHAR(5)    NOT NULL,
    TEAM_ID           INTEGER       NOT NULL,
    TEAM_ABBREVIATION CHAR(3)       NOT NULL,
    PLAYER_AGE        INTEGER,
    GP                INTEGER,
    GS                INTEGER,
    MIN               DECIMAL(10,1),
    FGM               INTEGER,
    FGA               INTEGER,
    FG_PCT            DECIMAL(5,3),
    FG3M              INTEGER,
    FG3A              INTEGER,
    FG3_PCT           DECIMAL(5,3),
    FTM               INTEGER,
    FTA               INTEGER,
    FT_PCT            DECIMAL(5,3),
    OREB              INTEGER,
    DREB              INTEGER,
    REB               INTEGER,
    AST               INTEGER,
    STL               INTEGER,
    BLK               INTEGER,
    TOV               INTEGER,
    PF                INTEGER,
    PTS               INTEGER,
    PRIMARY KEY (PLAYER_ID, SEASON_ID, TEAM_ID),
    FOREIGN KEY (PLAYER_ID) REFERENCES players(id),
    FOREIGN KEY (TEAM_ID) REFERENCES teams(id)
);

CREATE INDEX idx_player_career_stats_player ON player_career_stats(PLAYER_ID);
CREATE INDEX idx_player_career_stats_season ON player_career_stats(SEASON_ID);
CREATE INDEX idx_player_career_stats_team ON player_career_stats(TEAM_ID);
```

---

### Player Box Scores

**CLI Command:** `python fetch.py player-boxscores --game-id <GAME_ID>`

**Description:** Contains individual player box score statistics for a specific game. Each row represents one player's performance in a game, with players from both teams included.

#### Schema

| Column            | SQL Type       | Nullable | Description                                          |
|-------------------|----------------|----------|------------------------------------------------------|
| `GAME_ID`         | VARCHAR(10)    | NOT NULL | Unique game identifier                               |
| `PLAYER_ID`       | INTEGER        | NOT NULL | **Foreign Key** to `players.id`                      |
| `PLAYER_NAME`     | VARCHAR(100)   | NOT NULL | Player's full display name                           |
| `TEAM_ID`         | INTEGER        | NOT NULL | **Foreign Key** to `teams.id`                        |
| `TEAM_ABBREVIATION`| CHAR(3)       | NOT NULL | Three-letter team abbreviation                       |
| `MIN`             | VARCHAR(10)    | NULL     | Minutes played (format: "MM:SS")                     |
| `PTS`             | INTEGER        | NULL     | Points scored                                        |
| `REB`             | INTEGER        | NULL     | Total rebounds                                       |
| `AST`             | INTEGER        | NULL     | Assists                                              |
| `STL`             | INTEGER        | NULL     | Steals                                               |
| `BLK`             | INTEGER        | NULL     | Blocks                                               |
| `TOV`             | INTEGER        | NULL     | Turnovers                                            |
| `PF`              | INTEGER        | NULL     | Personal fouls                                       |
| `PLUS_MINUS`      | INTEGER        | NULL     | Plus/minus rating for the game                       |
| `FGM`             | INTEGER        | NULL     | Field goals made                                     |
| `FGA`             | INTEGER        | NULL     | Field goals attempted                                |
| `FG_PCT`          | DECIMAL(5,3)   | NULL     | Field goal percentage                                |
| `FG3M`            | INTEGER        | NULL     | Three-point field goals made                         |
| `FG3A`            | INTEGER        | NULL     | Three-point field goals attempted                    |
| `FG3_PCT`         | DECIMAL(5,3)   | NULL     | Three-point field goal percentage                    |
| `FTM`             | INTEGER        | NULL     | Free throws made                                     |
| `FTA`             | INTEGER        | NULL     | Free throws attempted                                |
| `FT_PCT`          | DECIMAL(5,3)   | NULL     | Free throw percentage                                |

#### SQL DDL

```sql
CREATE TABLE player_box_scores (
    GAME_ID           VARCHAR(10)   NOT NULL,
    PLAYER_ID         INTEGER       NOT NULL,
    PLAYER_NAME       VARCHAR(100)  NOT NULL,
    TEAM_ID           INTEGER       NOT NULL,
    TEAM_ABBREVIATION CHAR(3)       NOT NULL,
    MIN               VARCHAR(10),
    PTS               INTEGER,
    REB               INTEGER,
    AST               INTEGER,
    STL               INTEGER,
    BLK               INTEGER,
    TOV               INTEGER,
    PF                INTEGER,
    PLUS_MINUS        INTEGER,
    FGM               INTEGER,
    FGA               INTEGER,
    FG_PCT            DECIMAL(5,3),
    FG3M              INTEGER,
    FG3A              INTEGER,
    FG3_PCT           DECIMAL(5,3),
    FTM               INTEGER,
    FTA               INTEGER,
    FT_PCT            DECIMAL(5,3),
    PRIMARY KEY (GAME_ID, PLAYER_ID),
    FOREIGN KEY (PLAYER_ID) REFERENCES players(id),
    FOREIGN KEY (TEAM_ID) REFERENCES teams(id)
);

CREATE INDEX idx_player_box_scores_game ON player_box_scores(GAME_ID);
CREATE INDEX idx_player_box_scores_player ON player_box_scores(PLAYER_ID);
CREATE INDEX idx_player_box_scores_team ON player_box_scores(TEAM_ID);
```

#### Sample Data

| GAME_ID    | PLAYER_ID | PLAYER_NAME   | TEAM_ABBREVIATION | PTS | REB | AST |
|------------|-----------|---------------|-------------------|-----|-----|-----|
| 0022400123 | 2544      | LeBron James  | LAL               | 32  | 8   | 11  |
| 0022400123 | 201939    | Stephen Curry | GSW               | 28  | 5   | 7   |

---

### Team Game Box Scores

**CLI Command:** `python fetch.py team-game-boxscores --team-id <ID> --date-from <DATE> --date-to <DATE>`

**Description:** Contains team-level game statistics retrieved via LeagueGameFinder. Each row represents one team's performance in a game within the specified date range or season. This provides team box scores for games filtered by date range and/or season.

#### Schema

| Column          | SQL Type       | Nullable | Description                                          |
|-----------------|----------------|----------|------------------------------------------------------|
| `SEASON_ID`     | VARCHAR(10)    | NOT NULL | Season identifier (e.g., "22023" for 2023-24)        |
| `TEAM_ID`       | INTEGER        | NOT NULL | **Foreign Key** to `teams.id`                        |
| `TEAM_ABBREVIATION`| CHAR(3)     | NOT NULL | Three-letter team abbreviation                       |
| `TEAM_NAME`     | VARCHAR(50)    | NOT NULL | Full team name                                       |
| `GAME_ID`       | VARCHAR(10)    | NOT NULL | Unique game identifier                               |
| `GAME_DATE`     | DATE           | NOT NULL | Date the game was played                             |
| `MATCHUP`       | VARCHAR(20)    | NOT NULL | Game matchup (e.g., "LAL vs. GSW" or "LAL @ BOS")    |
| `WL`            | CHAR(1)        | NULL     | Win/Loss indicator ("W" or "L")                      |
| `MIN`           | INTEGER        | NULL     | Total minutes played by team                         |
| `PTS`           | INTEGER        | NULL     | Points scored                                        |
| `FGM`           | INTEGER        | NULL     | Field goals made                                     |
| `FGA`           | INTEGER        | NULL     | Field goals attempted                                |
| `FG_PCT`        | DECIMAL(5,3)   | NULL     | Field goal percentage                                |
| `FG3M`          | INTEGER        | NULL     | Three-point field goals made                         |
| `FG3A`          | INTEGER        | NULL     | Three-point field goals attempted                    |
| `FG3_PCT`       | DECIMAL(5,3)   | NULL     | Three-point field goal percentage                    |
| `FTM`           | INTEGER        | NULL     | Free throws made                                     |
| `FTA`           | INTEGER        | NULL     | Free throws attempted                                |
| `FT_PCT`        | DECIMAL(5,3)   | NULL     | Free throw percentage                                |
| `OREB`          | INTEGER        | NULL     | Offensive rebounds                                   |
| `DREB`          | INTEGER        | NULL     | Defensive rebounds                                   |
| `REB`           | INTEGER        | NULL     | Total rebounds                                       |
| `AST`           | INTEGER        | NULL     | Assists                                              |
| `STL`           | INTEGER        | NULL     | Steals                                               |
| `BLK`           | INTEGER        | NULL     | Blocks                                               |
| `TOV`           | INTEGER        | NULL     | Turnovers                                            |
| `PF`            | INTEGER        | NULL     | Personal fouls                                       |
| `PLUS_MINUS`    | INTEGER        | NULL     | Plus/minus rating for the game                       |

#### SQL DDL

```sql
CREATE TABLE team_game_box_scores (
    SEASON_ID         VARCHAR(10)   NOT NULL,
    TEAM_ID           INTEGER       NOT NULL,
    TEAM_ABBREVIATION CHAR(3)       NOT NULL,
    TEAM_NAME         VARCHAR(50)   NOT NULL,
    GAME_ID           VARCHAR(10)   NOT NULL,
    GAME_DATE         DATE          NOT NULL,
    MATCHUP           VARCHAR(20)   NOT NULL,
    WL                CHAR(1),
    MIN               INTEGER,
    PTS               INTEGER,
    FGM               INTEGER,
    FGA               INTEGER,
    FG_PCT            DECIMAL(5,3),
    FG3M              INTEGER,
    FG3A              INTEGER,
    FG3_PCT           DECIMAL(5,3),
    FTM               INTEGER,
    FTA               INTEGER,
    FT_PCT            DECIMAL(5,3),
    OREB              INTEGER,
    DREB              INTEGER,
    REB               INTEGER,
    AST               INTEGER,
    STL               INTEGER,
    BLK               INTEGER,
    TOV               INTEGER,
    PF                INTEGER,
    PLUS_MINUS        INTEGER,
    PRIMARY KEY (TEAM_ID, GAME_ID),
    FOREIGN KEY (TEAM_ID) REFERENCES teams(id)
);

CREATE INDEX idx_team_game_box_scores_season ON team_game_box_scores(SEASON_ID);
CREATE INDEX idx_team_game_box_scores_team ON team_game_box_scores(TEAM_ID);
CREATE INDEX idx_team_game_box_scores_date ON team_game_box_scores(GAME_DATE);
CREATE INDEX idx_team_game_box_scores_game ON team_game_box_scores(GAME_ID);
```

#### Sample Data

| GAME_ID    | TEAM_ABBREVIATION | GAME_DATE  | MATCHUP      | WL | PTS | REB | AST |
|------------|-------------------|------------|--------------|-----|-----|-----|-----|
| 0022400123 | LAL               | 2024-01-15 | LAL vs. GSW  | W   | 118 | 45  | 28  |
| 0022400123 | GSW               | 2024-01-15 | GSW @ LAL    | L   | 112 | 42  | 25  |

---

## Statistics Glossary

| Abbreviation | Full Name                      | Description                                    |
|--------------|--------------------------------|------------------------------------------------|
| GP           | Games Played                   | Number of games participated in                |
| GS           | Games Started                  | Number of games started                        |
| MIN          | Minutes                        | Minutes played                                 |
| FGM          | Field Goals Made               | Successful field goal attempts                 |
| FGA          | Field Goals Attempted          | Total field goal attempts                      |
| FG_PCT       | Field Goal Percentage          | FGM / FGA                                      |
| FG3M         | 3-Point Field Goals Made       | Successful 3-point attempts                    |
| FG3A         | 3-Point Field Goals Attempted  | Total 3-point attempts                         |
| FG3_PCT      | 3-Point Field Goal Percentage  | FG3M / FG3A                                    |
| FTM          | Free Throws Made               | Successful free throw attempts                 |
| FTA          | Free Throws Attempted          | Total free throw attempts                      |
| FT_PCT       | Free Throw Percentage          | FTM / FTA                                      |
| OREB         | Offensive Rebounds             | Rebounds on offense                            |
| DREB         | Defensive Rebounds             | Rebounds on defense                            |
| REB          | Total Rebounds                 | OREB + DREB                                    |
| AST          | Assists                        | Passes leading to scores                       |
| STL          | Steals                         | Turnovers forced from opponents                |
| BLK          | Blocks                         | Opponent shots blocked                         |
| TOV          | Turnovers                      | Ball lost to opponents                         |
| PF           | Personal Fouls                 | Fouls committed                                |
| PTS          | Points                         | Total points scored                            |
| PLUS_MINUS   | Plus/Minus                     | Point differential while on court              |
| WL           | Win/Loss                       | Game result indicator                          |

---

## Usage Examples

### Fetch all players and load into a database

```bash
# Generate CSV
python fetch.py players --output data/players.csv

# Load into SQLite
sqlite3 nba.db <<EOF
.mode csv
.import data/players.csv players
EOF
```

### Query player game logs

```sql
-- Find LeBron James' best scoring games in 2022-23
SELECT GAME_DATE, MATCHUP, PTS, REB, AST, PLUS_MINUS
FROM player_game_logs
WHERE Player_ID = 2544
  AND SEASON_ID LIKE '%2022%'
ORDER BY PTS DESC
LIMIT 10;
```

### Join players with career stats

```sql
-- Get career averages for active players
SELECT 
    p.full_name,
    pcs.SEASON_ID,
    pcs.TEAM_ABBREVIATION,
    ROUND(pcs.PTS * 1.0 / pcs.GP, 1) as PPG,
    ROUND(pcs.REB * 1.0 / pcs.GP, 1) as RPG,
    ROUND(pcs.AST * 1.0 / pcs.GP, 1) as APG
FROM players p
JOIN player_career_stats pcs ON p.id = pcs.PLAYER_ID
WHERE p.is_active = TRUE
ORDER BY PPG DESC;
```

### Query player box scores for a game

```bash
# Fetch player box scores for a specific game
python fetch.py player-boxscores --game-id 0022400123 --output data/player_boxscores.csv
```

```sql
-- Find top scorers in a specific game
SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST, FG_PCT
FROM player_box_scores
WHERE GAME_ID = '0022400123'
ORDER BY PTS DESC;
```

### Query team game box scores

```bash
# Fetch Lakers games in January 2024
python fetch.py team-game-boxscores --team-id LAL --date-from 2024-01-01 --date-to 2024-01-31 --output data/lakers_jan_2024.csv
```

```sql
-- Find team's highest scoring games in a date range
SELECT GAME_DATE, MATCHUP, WL, PTS, FG_PCT, FG3_PCT
FROM team_game_box_scores
WHERE TEAM_ID = 1610612747
ORDER BY PTS DESC
LIMIT 5;
```

---

## Notes

- **Primary Keys**: Most tables use composite primary keys based on entity IDs and game/season identifiers.
- **Foreign Keys**: Player and team IDs link to the base `players` and `teams` tables.
- **Nullable Fields**: Statistics columns are nullable to handle cases where data may be missing.
- **Data Types**: DECIMAL types are used for percentages to maintain precision.
- **Indexes**: Suggested indexes are provided for common query patterns.
