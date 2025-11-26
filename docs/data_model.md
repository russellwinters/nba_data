# NBA Data Model Documentation

This document describes the data structures returned by the NBA Data CLI commands, modeled as SQL database tables. Each entity represents the structure of the CSV output from the corresponding CLI command.

## Table of Contents

- [Overview](#overview)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Tables](#tables)
  - [Players](#players)
  - [Teams](#teams)
  - [Player Game Logs](#player-game-logs)
  - [Team Game Logs](#team-game-logs)
  - [Team Game Logs (Extended)](#team-game-logs-extended)
  - [Player Career Stats](#player-career-stats)

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
┌─────────────┐         ┌─────────────────────┐
│   Players   │         │       Teams         │
├─────────────┤         ├─────────────────────┤
│ PK: id      │         │ PK: id              │
│ full_name   │         │ full_name           │
│ first_name  │         │ abbreviation        │
│ last_name   │         │ nickname            │
│ is_active   │         │ city                │
└──────┬──────┘         │ state               │
       │                │ year_founded        │
       │                └──────────┬──────────┘
       │                           │
       ▼                           ▼
┌──────────────────────┐   ┌──────────────────────┐
│  Player Game Logs    │   │   Team Game Logs     │
├──────────────────────┤   ├──────────────────────┤
│ PK: (Player_ID,      │   │ PK: (Team_ID,        │
│      Game_ID)        │   │      Game_ID)        │
│ FK: Player_ID        │   │ FK: Team_ID          │
│ SEASON_ID            │   │ GAME_DATE            │
│ GAME_DATE            │   │ MATCHUP              │
│ MATCHUP              │   │ WL                   │
│ Stats columns...     │   │ Stats columns...     │
└──────────────────────┘   └──────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Player Career Stats  │
├──────────────────────┤
│ PK: (PLAYER_ID,      │
│      SEASON_ID,      │
│      TEAM_ID)        │
│ FK: PLAYER_ID        │
│ FK: TEAM_ID          │
│ Career stats...      │
└──────────────────────┘
```

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

### Team Game Logs

**CLI Command:** `python fetch.py team-games --team-id <ABBREVIATION> --season <SEASON>`

**Description:** Contains per-game statistics for a specific team during a given season. Each row represents one game played by the team.

#### Schema

| Column      | SQL Type       | Nullable | Description                                          |
|-------------|----------------|----------|------------------------------------------------------|
| `Team_ID`   | INTEGER        | NOT NULL | **Foreign Key** to `teams.id`                        |
| `Game_ID`   | VARCHAR(10)    | NOT NULL | Unique game identifier                               |
| `GAME_DATE` | DATE           | NOT NULL | Date the game was played                             |
| `MATCHUP`   | VARCHAR(20)    | NOT NULL | Game matchup (e.g., "LAL vs. GSW" or "LAL @ BOS")    |
| `WL`        | CHAR(1)        | NULL     | Win/Loss indicator ("W" or "L")                      |
| `W`         | INTEGER        | NULL     | Cumulative wins in the season                        |
| `L`         | INTEGER        | NULL     | Cumulative losses in the season                      |
| `W_PCT`     | DECIMAL(5,3)   | NULL     | Win percentage                                       |
| `MIN`       | INTEGER        | NULL     | Total minutes played by team                         |
| `FGM`       | INTEGER        | NULL     | Field goals made                                     |
| `FGA`       | INTEGER        | NULL     | Field goals attempted                                |
| `FG_PCT`    | DECIMAL(5,3)   | NULL     | Field goal percentage                                |
| `FG3M`      | INTEGER        | NULL     | Three-point field goals made                         |
| `FG3A`      | INTEGER        | NULL     | Three-point field goals attempted                    |
| `FG3_PCT`   | DECIMAL(5,3)   | NULL     | Three-point field goal percentage                    |
| `FTM`       | INTEGER        | NULL     | Free throws made                                     |
| `FTA`       | INTEGER        | NULL     | Free throws attempted                                |
| `FT_PCT`    | DECIMAL(5,3)   | NULL     | Free throw percentage                                |
| `OREB`      | INTEGER        | NULL     | Offensive rebounds                                   |
| `DREB`      | INTEGER        | NULL     | Defensive rebounds                                   |
| `REB`       | INTEGER        | NULL     | Total rebounds                                       |
| `AST`       | INTEGER        | NULL     | Assists                                              |
| `STL`       | INTEGER        | NULL     | Steals                                               |
| `BLK`       | INTEGER        | NULL     | Blocks                                               |
| `TOV`       | INTEGER        | NULL     | Turnovers                                            |
| `PF`        | INTEGER        | NULL     | Personal fouls                                       |
| `PTS`       | INTEGER        | NULL     | Points scored                                        |

#### SQL DDL

```sql
CREATE TABLE team_game_logs (
    Team_ID     INTEGER       NOT NULL,
    Game_ID     VARCHAR(10)   NOT NULL,
    GAME_DATE   DATE          NOT NULL,
    MATCHUP     VARCHAR(20)   NOT NULL,
    WL          CHAR(1),
    W           INTEGER,
    L           INTEGER,
    W_PCT       DECIMAL(5,3),
    MIN         INTEGER,
    FGM         INTEGER,
    FGA         INTEGER,
    FG_PCT      DECIMAL(5,3),
    FG3M        INTEGER,
    FG3A        INTEGER,
    FG3_PCT     DECIMAL(5,3),
    FTM         INTEGER,
    FTA         INTEGER,
    FT_PCT      DECIMAL(5,3),
    OREB        INTEGER,
    DREB        INTEGER,
    REB         INTEGER,
    AST         INTEGER,
    STL         INTEGER,
    BLK         INTEGER,
    TOV         INTEGER,
    PF          INTEGER,
    PTS         INTEGER,
    PRIMARY KEY (Team_ID, Game_ID),
    FOREIGN KEY (Team_ID) REFERENCES teams(id)
);

CREATE INDEX idx_team_game_logs_date ON team_game_logs(GAME_DATE);
CREATE INDEX idx_team_game_logs_team ON team_game_logs(Team_ID);
```

---

### Team Game Logs (Extended)

**CLI Command:** `python fetch.py team-game-logs --team-id <ID|ABBREVIATION|NAME> [--season <SEASON>] [--season-type <TYPE>]`

**Description:** Extended team game logs with additional fields including ranking information. This endpoint provides more flexible filtering options and additional statistical rankings.

#### Schema

| Column              | SQL Type       | Nullable | Description                                          |
|---------------------|----------------|----------|------------------------------------------------------|
| `SEASON_YEAR`       | VARCHAR(10)    | NOT NULL | Season identifier (e.g., "2022-23")                  |
| `TEAM_ID`           | INTEGER        | NOT NULL | **Foreign Key** to `teams.id`                        |
| `TEAM_ABBREVIATION` | CHAR(3)        | NOT NULL | Three-letter team abbreviation                       |
| `TEAM_NAME`         | VARCHAR(50)    | NOT NULL | Full team name                                       |
| `GAME_ID`           | VARCHAR(10)    | NOT NULL | Unique game identifier                               |
| `GAME_DATE`         | DATE           | NOT NULL | Date the game was played                             |
| `MATCHUP`           | VARCHAR(20)    | NOT NULL | Game matchup                                         |
| `WL`                | CHAR(1)        | NULL     | Win/Loss indicator                                   |
| `MIN`               | INTEGER        | NULL     | Minutes played                                       |
| `FGM`               | INTEGER        | NULL     | Field goals made                                     |
| `FGA`               | INTEGER        | NULL     | Field goals attempted                                |
| `FG_PCT`            | DECIMAL(5,3)   | NULL     | Field goal percentage                                |
| `FG3M`              | INTEGER        | NULL     | Three-point field goals made                         |
| `FG3A`              | INTEGER        | NULL     | Three-point field goals attempted                    |
| `FG3_PCT`           | DECIMAL(5,3)   | NULL     | Three-point field goal percentage                    |
| `FTM`               | INTEGER        | NULL     | Free throws made                                     |
| `FTA`               | INTEGER        | NULL     | Free throws attempted                                |
| `FT_PCT`            | DECIMAL(5,3)   | NULL     | Free throw percentage                                |
| `OREB`              | INTEGER        | NULL     | Offensive rebounds                                   |
| `DREB`              | INTEGER        | NULL     | Defensive rebounds                                   |
| `REB`               | INTEGER        | NULL     | Total rebounds                                       |
| `AST`               | INTEGER        | NULL     | Assists                                              |
| `TOV`               | INTEGER        | NULL     | Turnovers                                            |
| `STL`               | INTEGER        | NULL     | Steals                                               |
| `BLK`               | INTEGER        | NULL     | Blocks                                               |
| `BLKA`              | INTEGER        | NULL     | Blocked attempts (shots blocked by opponent)         |
| `PF`                | INTEGER        | NULL     | Personal fouls                                       |
| `PFD`               | INTEGER        | NULL     | Personal fouls drawn                                 |
| `PTS`               | INTEGER        | NULL     | Points scored                                        |
| `PLUS_MINUS`        | INTEGER        | NULL     | Plus/minus rating                                    |
| `GP_RANK`           | INTEGER        | NULL     | Games played rank                                    |
| `W_RANK`            | INTEGER        | NULL     | Wins rank                                            |
| `L_RANK`            | INTEGER        | NULL     | Losses rank                                          |
| `W_PCT_RANK`        | INTEGER        | NULL     | Win percentage rank                                  |
| `MIN_RANK`          | INTEGER        | NULL     | Minutes rank                                         |
| `FGM_RANK`          | INTEGER        | NULL     | Field goals made rank                                |
| `FGA_RANK`          | INTEGER        | NULL     | Field goals attempted rank                           |
| `FG_PCT_RANK`       | INTEGER        | NULL     | Field goal percentage rank                           |
| `FG3M_RANK`         | INTEGER        | NULL     | Three-point field goals made rank                    |
| `FG3A_RANK`         | INTEGER        | NULL     | Three-point field goals attempted rank               |
| `FG3_PCT_RANK`      | INTEGER        | NULL     | Three-point field goal percentage rank               |
| `FTM_RANK`          | INTEGER        | NULL     | Free throws made rank                                |
| `FTA_RANK`          | INTEGER        | NULL     | Free throws attempted rank                           |
| `FT_PCT_RANK`       | INTEGER        | NULL     | Free throw percentage rank                           |
| `OREB_RANK`         | INTEGER        | NULL     | Offensive rebounds rank                              |
| `DREB_RANK`         | INTEGER        | NULL     | Defensive rebounds rank                              |
| `REB_RANK`          | INTEGER        | NULL     | Total rebounds rank                                  |
| `AST_RANK`          | INTEGER        | NULL     | Assists rank                                         |
| `TOV_RANK`          | INTEGER        | NULL     | Turnovers rank                                       |
| `STL_RANK`          | INTEGER        | NULL     | Steals rank                                          |
| `BLK_RANK`          | INTEGER        | NULL     | Blocks rank                                          |
| `BLKA_RANK`         | INTEGER        | NULL     | Blocked attempts rank                                |
| `PF_RANK`           | INTEGER        | NULL     | Personal fouls rank                                  |
| `PFD_RANK`          | INTEGER        | NULL     | Personal fouls drawn rank                            |
| `PTS_RANK`          | INTEGER        | NULL     | Points rank                                          |
| `PLUS_MINUS_RANK`   | INTEGER        | NULL     | Plus/minus rank                                      |

#### SQL DDL

```sql
CREATE TABLE team_game_logs_extended (
    SEASON_YEAR       VARCHAR(10)   NOT NULL,
    TEAM_ID           INTEGER       NOT NULL,
    TEAM_ABBREVIATION CHAR(3)       NOT NULL,
    TEAM_NAME         VARCHAR(50)   NOT NULL,
    GAME_ID           VARCHAR(10)   NOT NULL,
    GAME_DATE         DATE          NOT NULL,
    MATCHUP           VARCHAR(20)   NOT NULL,
    WL                CHAR(1),
    MIN               INTEGER,
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
    TOV               INTEGER,
    STL               INTEGER,
    BLK               INTEGER,
    BLKA              INTEGER,
    PF                INTEGER,
    PFD               INTEGER,
    PTS               INTEGER,
    PLUS_MINUS        INTEGER,
    GP_RANK           INTEGER,
    W_RANK            INTEGER,
    L_RANK            INTEGER,
    W_PCT_RANK        INTEGER,
    MIN_RANK          INTEGER,
    FGM_RANK          INTEGER,
    FGA_RANK          INTEGER,
    FG_PCT_RANK       INTEGER,
    FG3M_RANK         INTEGER,
    FG3A_RANK         INTEGER,
    FG3_PCT_RANK      INTEGER,
    FTM_RANK          INTEGER,
    FTA_RANK          INTEGER,
    FT_PCT_RANK       INTEGER,
    OREB_RANK         INTEGER,
    DREB_RANK         INTEGER,
    REB_RANK          INTEGER,
    AST_RANK          INTEGER,
    TOV_RANK          INTEGER,
    STL_RANK          INTEGER,
    BLK_RANK          INTEGER,
    BLKA_RANK         INTEGER,
    PF_RANK           INTEGER,
    PFD_RANK          INTEGER,
    PTS_RANK          INTEGER,
    PLUS_MINUS_RANK   INTEGER,
    PRIMARY KEY (TEAM_ID, GAME_ID),
    FOREIGN KEY (TEAM_ID) REFERENCES teams(id)
);

CREATE INDEX idx_team_game_logs_ext_season ON team_game_logs_extended(SEASON_YEAR);
CREATE INDEX idx_team_game_logs_ext_date ON team_game_logs_extended(GAME_DATE);
CREATE INDEX idx_team_game_logs_ext_team ON team_game_logs_extended(TEAM_ID);
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
| BLKA         | Blocked Attempts               | Own shots blocked by opponents                 |
| TOV          | Turnovers                      | Ball lost to opponents                         |
| PF           | Personal Fouls                 | Fouls committed                                |
| PFD          | Personal Fouls Drawn           | Fouls drawn from opponents                     |
| PTS          | Points                         | Total points scored                            |
| PLUS_MINUS   | Plus/Minus                     | Point differential while on court              |
| WL           | Win/Loss                       | Game result indicator                          |
| W            | Wins                           | Cumulative wins                                |
| L            | Losses                         | Cumulative losses                              |
| W_PCT        | Win Percentage                 | W / (W + L)                                    |

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

---

## Notes

- **Primary Keys**: Most tables use composite primary keys based on entity IDs and game/season identifiers.
- **Foreign Keys**: Player and team IDs link to the base `players` and `teams` tables.
- **Nullable Fields**: Statistics columns are nullable to handle cases where data may be missing.
- **Data Types**: DECIMAL types are used for percentages to maintain precision.
- **Indexes**: Suggested indexes are provided for common query patterns.
