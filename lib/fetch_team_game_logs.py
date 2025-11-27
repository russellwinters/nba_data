"""Fetch team game logs using `nba_api.stats.endpoints.teamgamelogs.TeamGameLogs`.

This module provides a small wrapper around the NBA API endpoint and returns
a `pandas.DataFrame` for downstream processing.

Example:
    from lib.fetch_team_game_logs import fetch_team_game_logs

    df = fetch_team_game_logs('LAL', season='2022-23')
"""
from typing import Optional, Any

import pandas as pd
import argparse

from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.static import teams

from lib.helpers import handle_api_errors, log_error, log_info, log_warning


def _normalize_team_id(team_id: Any) -> int:
    """Resolve a numeric team id or common string forms to the numeric team id.

    Accepts an int (returned as-is), a numeric string (converted to int), a
    team abbreviation (e.g. 'LAL'), or a full team name. Raises `ValueError`
    if the team cannot be resolved.
    """
    if team_id is None:
        raise ValueError("team_id is required")

    # Already numeric
    if isinstance(team_id, int):
        return team_id

    # Numeric string
    if isinstance(team_id, str) and team_id.isdigit():
        return int(team_id)

    # Try abbreviation (common usage in this repo)
    if isinstance(team_id, str):
        team_abbr = team_id.strip().upper()
        found = teams.find_team_by_abbreviation(team_abbr)
        if found:
            return found["id"]

        # Try full name lookup
        try:
            found = teams.find_team_by_full_name(team_id.strip())
            if found:
                return found["id"]
        except Exception:
            pass

    raise ValueError(f"Could not resolve team_id: {team_id!r}")


@handle_api_errors
def fetch_team_game_logs(
    team_id: Any,
    season: Optional[str] = None,
    *,
    season_type: Optional[str] = None,
    timeout: int = 30,
    proxy: Optional[str] = None,
    headers: Optional[dict] = None,
    get_request: bool = True,
    output_path: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch team game logs and return a `pandas.DataFrame`.

    Args:
        team_id: Team id (int), numeric string, abbreviation (e.g. 'LAL'), or full name.
        season: Optional season string forwarded to `season_nullable` (e.g. '2022-23').
        season_type: Optional season type forwarded to `season_type_nullable` (e.g. 'Regular Season').
        timeout: Request timeout in seconds.
        proxy: Optional proxy URL passed to the endpoint.
        headers: Optional headers dict passed to the endpoint.
        get_request: Whether to execute the request (passed to nba_api).
        output_path: Optional path to save the resulting CSV. If not provided a
            default path of `data/team_{ABBR}_games_{season}.csv` will be used
            when possible (ABBR falls back to the numeric team id).

    Returns:
        `pandas.DataFrame` with the first DataFrame returned by the endpoint, or
        an empty DataFrame when no data is available or on invalid inputs.

    Notes:
        This wrapper intentionally returns an empty DataFrame for invalid
        `team_id` values (with a warning) to match the tolerant behavior used
        elsewhere in this project.
    """
    try:
        team_id_num = _normalize_team_id(team_id)
    except ValueError as e:
        # Print a clear, repo-consistent diagnostic and return an empty DataFrame
        log_error(f"Could not resolve team_id: {team_id!r}", {"error": str(e)})
        return pd.DataFrame()

    request_kwargs = {}
    if season is not None:
        request_kwargs["season_nullable"] = season
    if season_type is not None:
        request_kwargs["season_type_nullable"] = season_type

    # Try several constructor signatures to be tolerant to different
    # `nba_api` versions which have changed parameter names over time.
    transport_args = {}
    if timeout is not None:
        transport_args["timeout"] = timeout
    if proxy is not None:
        transport_args["proxy"] = proxy
    if headers is not None:
        transport_args["headers"] = headers
    if get_request is not None:
        transport_args["get_request"] = get_request

    endpoint = None
    last_exc = None
    # Try common variants in order of preference
    # 1) Full kwargs including transport options
    try:
        kwargs = {**request_kwargs, **transport_args, "team_id": team_id_num}
        endpoint = teamgamelogs.TeamGameLogs(**kwargs)
    except Exception as e:
        last_exc = e

    # 2) Same as above but without transport args (older nba_api)
    if endpoint is None:
        try:
            kwargs = {**request_kwargs, "team_id": team_id_num}
            endpoint = teamgamelogs.TeamGameLogs(**kwargs)
        except Exception as e:
            last_exc = e

    # 3) Positional first arg (some versions expect positional team id)
    if endpoint is None:
        try:
            endpoint = teamgamelogs.TeamGameLogs(team_id_num, **request_kwargs)
        except Exception as e:
            last_exc = e

    # 4) Alternate parameter name used by some signatures
    if endpoint is None:
        try:
            kwargs = {**request_kwargs, "team_id_nullable": team_id_num}
            endpoint = teamgamelogs.TeamGameLogs(**kwargs)
        except Exception as e:
            last_exc = e

    # 5) Last-ditch: try positional without any extra kwargs
    if endpoint is None:
        try:
            endpoint = teamgamelogs.TeamGameLogs(team_id_num)
        except Exception as e:
            last_exc = e
    if endpoint is None:
        log_error("Failed to construct TeamGameLogs endpoint with known signatures", {"last_error": str(last_exc)})
        return pd.DataFrame()

    # Diagnostic: show what we found for the requested team (consistent with other lib modules)
    try:
        if hasattr(endpoint, 'parameters'):
            try:
                log_info(f"Request parameters: {endpoint.parameters}")
            except Exception:
                pass
        if getattr(endpoint, 'nba_response', None) is not None:
            try:
                norm = endpoint.nba_response.get_normalized_dict()
                log_info(f"NBA response keys: {list(norm.keys())}")
            except Exception:
                pass
    except Exception:
        # Keep the demo tolerant; diagnostics are best-effort only
        pass

    try:
        dfs = endpoint.get_data_frames()
    except Exception as e:
        log_error("Failed to retrieve data frames from TeamGameLogs endpoint", {"error": str(e)})
        return pd.DataFrame()

    if not dfs:
        return pd.DataFrame()

    df = dfs[0]
    if df is None:
        return pd.DataFrame()

    # Determine a sensible default output path similar to `fetch_team_games`.
    # Prefer the team abbreviation when available; fallback to numeric id.
    team_abbr = None
    try:
        # `teams.find_team_by_id` may not exist on very old nba_api versions;
        # guard the call.
        if hasattr(teams, 'find_team_by_id'):
            info = teams.find_team_by_id(team_id_num)
            if info and isinstance(info, dict):
                team_abbr = info.get('abbreviation')
    except Exception:
        team_abbr = None

    if output_path is None:
        season_part = season if season is not None else "all"
        output_path = f'data/team_{team_abbr or team_id_num}_games_{season_part}.csv'

    # Try to write the DataFrame (including empty ones) to CSV so downstream
    # steps are reproducible and consistent with `fetch_team_games`.
    try:
        df.to_csv(output_path, index=False)
        try:
            rows, cols = df.shape
            log_info(f"Wrote {output_path} ({rows} rows, {cols} cols)")
        except Exception:
            log_info(f"Wrote {output_path}")
        try:
            print(df.head())
        except Exception:
            pass
    except Exception as e:
        log_error(f"Failed to write CSV to {output_path}", {"error": str(e)})

    return df


def main():
    parser = argparse.ArgumentParser(description="Fetch a team's game logs for a specific season")
    parser.add_argument(
        "--team-id",
        dest="team_id",
        required=True,
        help="Team identifier: numeric id, abbreviation (e.g. 'LAL'), or full team name",
    )
    parser.add_argument(
        "--season",
        help='Season string (e.g., "2022-23"). Optional; forwarded to the endpoint as season_nullable',
    )
    parser.add_argument(
        "--output",
        help='Output CSV file path (optional). If provided, saves DataFrame to this path',
    )
    args = parser.parse_args()
    # Pass `args.output` into the function; the function will write the
    # DataFrame to the provided path or compute a default path when none
    # is supplied. Avoid double-writing here.
    fetch_team_game_logs(team_id=args.team_id, season=args.season, output_path=args.output)
    

if __name__ == "__main__":
    main()
