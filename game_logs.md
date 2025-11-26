## Game Logs

This document provides an overview of the game logs available through the NBA API.

**One-line Summary**: `TeamGameLog` fetches a single team's game-by-game stats; `TeamGameLogs` provides a more flexible, multi-filtered game-log query across teams/players.

**Short Explanation**
- **TeamGameLog**: A focused endpoint to retrieve game-by-game totals for a single team. The constructor requires a `team_id` and accepts season/date filters and a `SeasonType` selector.
- **TeamGameLogs**: A broader, filterable endpoint (plural) that accepts many optional filters such as date range, opponent, location, last N games, outcome, month, season segment, etc. Use this when you need to search game logs across teams or apply multiple filters.

**Usage & Parameters**

- **Import (both endpoints)**: `from nba_api.stats.endpoints import teamgamelog, teamgamelogs`

- **TeamGameLog**:
	- **Constructor signature (key params)**: `TeamGameLog(team_id, season=Season.default, season_type_all_star=SeasonTypeAllStar.default, date_from_nullable="", date_to_nullable="", league_id_nullable=LeagueIDNullable.default, proxy=None, headers=None, timeout=30, get_request=True)`
	- **Meaning**:
		- **team_id**: (required) NBA team id (integer)
		- **season**: season string (e.g. `'2022-23'`) — uses `Season` parameter helper by default
		- **season_type_all_star**: selects season type (e.g. `'Regular Season'`, `'Playoffs'`) via `SeasonTypeAllStar`
		- **date_from_nullable / date_to_nullable**: optional date range filters (strings)
		- **league_id_nullable**: usually defaults to the NBA league id
		- **proxy / headers / timeout**: request options
		- **get_request**: if `True` (default), the HTTP request will be made during construction; set to `False` to build the object and call `get_request()` later.
	- **Example**:
		```python
		from nba_api.stats.endpoints import teamgamelog

		tg = teamgamelog.TeamGameLog(team_id=1610612747, season='2022-23')
		# DataSet object is available as `tg.team_game_log`
		df = tg.team_game_log.get_data_frame()
		```

- **TeamGameLogs** (plural, more filters):
	- **Constructor signature (key params)**:
		`TeamGameLogs(date_from_nullable="", date_to_nullable="", game_segment_nullable=GameSegmentNullable.default, last_n_games_nullable=LastNGamesNullable.default, league_id_nullable=LeagueIDNullable.default, location_nullable=LocationNullable.default, measure_type_player_game_logs_nullable=None, month_nullable=MonthNullable.default, opp_team_id_nullable=None, outcome_nullable=OutcomeNullable.default, po_round_nullable="", per_mode_simple_nullable=PerModeSimpleNullable.default, period_nullable=PeriodNullable.default, player_id_nullable="", season_nullable=SeasonNullable.default, season_segment_nullable=SeasonSegmentNullable.default, season_type_nullable=SeasonTypeNullable.default, shot_clock_range_nullable=ShotClockRangeNullable.default, team_id_nullable="", vs_conference_nullable=ConferenceNullable.default, vs_division_nullable=DivisionNullable.default, proxy=None, headers=None, timeout=30, get_request=True)`
	- **Meaning / notable filters**:
		- **DateFrom / DateTo**: limit by date range
		- **LastNGames**: return only the last N games
		- **Location**: home/away filter
		- **OppTeamID**: filter by opponent team id
		- **Outcome**: Win/Loss filter
		- **TeamID / PlayerID**: you can target a specific team or player (nullable)
		- **Season / SeasonType / SeasonSegment / Month / Period / ShotClockRange / GameSegment**: additional sports-specific filters
		- All constructor parameters map to request keys like `DateFrom`, `DateTo`, `TeamID`, `Season`, etc.
	- **Example**:
		```python
		from nba_api.stats.endpoints import teamgamelogs

		tgl = teamgamelogs.TeamGameLogs(team_id_nullable=1610612747, season_nullable='2022-23', location_nullable='Home')
		df = tgl.team_game_logs.get_data_frame()
		```

**Notes & Best-Practices**
- Parameter helpers: the package exposes parameter helper objects (e.g. `Season`, `SeasonTypeNullable`, `LocationNullable`) with `.default` values — you can pass either those helpers or plain strings/integers depending on your needs.
- `get_request`: set to `False` in the constructor when you want to modify `.parameters` or headers (for proxy/auth) before calling the API via `.get_request()`.
- Response access: after request, the endpoint exposes a DataSet attribute (`team_game_log` or `team_game_logs`) — call `.get_data_frame()` on it to get a pandas DataFrame.
- Rate limiting / politeness: `nba_api` wraps NBA.com endpoints; respect rate limits and use reasonable `timeout` and optional sleeps between requests. The library supports `proxy` and custom `headers` if you need to route or throttle requests.

**Sources**
1. `nba_api` endpoint source: `teamgamelog.py` (constructor & parameters) — https://raw.githubusercontent.com/swar/nba_api/master/src/nba_api/stats/endpoints/teamgamelog.py (used for parameter names and defaults)
2. `nba_api` endpoint source: `teamgamelogs.py` (constructor & parameters) — https://raw.githubusercontent.com/swar/nba_api/master/src/nba_api/stats/endpoints/teamgamelogs.py (used for the full set of filterable parameters)
3. `nba_api` docs endpoints index — https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints (reference list of team endpoints)

Confidence: high — these details come from the package source code (links above).

If you want, I can:
- Add a snippet that demonstrates `get_request=False` usage and modifying headers before the request.
- Add common `TeamID` values (team id mapping) or a helper to look up team ids using `nba_api`'s teams static data.
