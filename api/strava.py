import sys
import os
import json
import time
import datetime
import configparser
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import refresh_token as _refresh_token

config = configparser.RawConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.properties"))
config_dict = dict(config.items("CONFIG"))

GOAL = float(config_dict["goal"])
YEAR_START = int(config_dict["year_start"])
TOP = int(config_dict["top"])
LONGCHAMP_SEGMENTS = [3572501, 17109958]

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CURRENT_TTL = 3600  # seconds — only applied to in-progress periods
ACTIVITY_CACHE_VERSION = 1
ACTIVITY_SYNC_OVERLAP = datetime.timedelta(days=3)


def _cache_path(key: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{key}.json")


def _cache_get(key: str, permanent: bool = False):
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    if not permanent and time.time() - os.path.getmtime(path) > CURRENT_TTL:
        return None
    with open(path) as f:
        return json.load(f)


def _cache_get_ytd(key: str, current_year: bool):
    path = _cache_path(key)
    if not os.path.exists(path):
        return None

    modified_at = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    if current_year:
        if time.time() - os.path.getmtime(path) > CURRENT_TTL:
            return None
    elif modified_at.date() != datetime.date.today():
        # The historical data is fixed, but the YTD cutoff advances daily.
        return None

    with open(path) as f:
        return json.load(f)


def _cache_set(key: str, data) -> None:
    with open(_cache_path(key), "w") as f:
        json.dump(data, f)


def _headers():
    token = _refresh_token()
    return {"Authorization": f"Bearer {token}"}


def _get(url: str, params: dict, headers: dict):
    for attempt in range(4):
        resp = requests.get(url, params=params, headers=headers, timeout=300)
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)  # 60s, 120s, 180s, 240s
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        return resp.json()
    return resp.json()  # return last response after all retries


def _get_activities(start: datetime.datetime, end: datetime.datetime, headers: dict) -> list:
    start_epoch = (start - datetime.datetime(1970, 1, 1)).total_seconds()
    end_epoch = (end - datetime.datetime(1970, 1, 1)).total_seconds()
    all_activities = []
    page = 1
    while True:
        data = _get(
            "https://www.strava.com/api/v3/athlete/activities",
            {"before": end_epoch, "after": start_epoch, "page": page, "per_page": "200"},
            headers,
        )
        if not isinstance(data, list):
            raise RuntimeError(f"Strava API error: {data}")
        all_activities.extend(data)
        if len(data) < 200:
            break
        page += 1
        time.sleep(0.3)
    return all_activities


def _activity_start_local(activity: dict) -> datetime.datetime:
    value = activity.get("start_date_local") or activity["start_date"]
    return datetime.datetime.fromisoformat(value.rstrip("Z"))


def _load_activity_cache(year: int):
    path = _cache_path(f"activities_{year}")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        if (
            data.get("version") != ACTIVITY_CACHE_VERSION
            or data.get("year") != year
            or not isinstance(data.get("activities"), list)
            or not data.get("fetched_until")
        ):
            return None
        return data
    except (OSError, ValueError, TypeError):
        return None


def _save_activity_cache(year: int, fetched_until: datetime.datetime, activities: list) -> None:
    _cache_set(
        f"activities_{year}",
        {
            "version": ACTIVITY_CACHE_VERSION,
            "year": year,
            "fetched_until": fetched_until.isoformat(),
            "activities": activities,
        },
    )


def _merge_activity_window(cached: list, refreshed: list, refresh_start: datetime.datetime) -> list:
    # Keep the stable part of the cache and replace the overlap window. This
    # picks up recent edits while activity IDs prevent duplicates.
    retained = [activity for activity in cached if _activity_start_local(activity) <= refresh_start]
    merged = {}
    for activity in retained + refreshed:
        key = activity.get("id")
        if key is None:
            key = (
                activity.get("start_date"),
                activity.get("name"),
                activity.get("distance"),
            )
        merged[key] = activity
    return sorted(merged.values(), key=_activity_start_local)


def _get_year_activities(year: int, headers: dict) -> list:
    year_start = datetime.datetime(year, 1, 1)
    year_end = datetime.datetime(year + 1, 1, 1)
    now = datetime.datetime.today()
    target_end = min(now, year_end)
    current = year == now.year
    cache = _load_activity_cache(year)

    if cache is None:
        activities = _get_activities(year_start, target_end, headers)
        _save_activity_cache(year, target_end, activities)
        return activities

    activities = cache["activities"]
    fetched_until = datetime.datetime.fromisoformat(cache["fetched_until"])
    cache_age = time.time() - os.path.getmtime(_cache_path(f"activities_{year}"))

    if (current and cache_age <= CURRENT_TTL) or (not current and fetched_until >= year_end):
        return activities

    refresh_start = max(year_start, fetched_until - ACTIVITY_SYNC_OVERLAP)
    refreshed = _get_activities(refresh_start, target_end, headers)
    activities = _merge_activity_window(activities, refreshed, refresh_start)
    _save_activity_cache(year, target_end, activities)
    return activities


def _load_gear_cache() -> dict:
    return _cache_get("gear_names", permanent=True) or {}


def _save_gear_cache(gear_cache: dict) -> None:
    _cache_set("gear_names", gear_cache)


def _resolve_gear(gid: str, headers: dict, gear_cache: dict) -> str:
    if gid in gear_cache:
        cached = gear_cache[gid]
        # re-fetch if previously cached as a raw ID (failed lookup)
        if cached != gid:
            return cached
    try:
        data = _get(f"https://www.strava.com/api/v3/gear/{gid}", {}, headers)
        name = data.get("name") if isinstance(data, dict) else None
        if not name:
            return gear_cache.get(gid, gid)
    except Exception:
        return gear_cache.get(gid, gid)
    gear_cache[gid] = name
    _save_gear_cache(gear_cache)
    return name


CYCLING_SPORT_TYPES = {"Ride", "VirtualRide", "GravelRide", "MountainBikeRide", "EBikeRide", "EMountainBikeRide"}


def _summarise_activities(activities: list, headers: dict, gear_cache: dict, full: bool = False) -> dict:
    total_distance = 0.0
    count = 0
    elevation = 0.0
    moving_time = 0
    commute_distance = 0.0
    gears: dict = {}
    act_types: dict = {}

    for act in activities:
        sport_type = act.get("sport_type") or act["type"]
        if sport_type not in CYCLING_SPORT_TYPES:
            continue
        is_virtual = sport_type == "VirtualRide"
        count += 1
        dist = float(act["distance"])
        elev = float(act["total_elevation_gain"])
        mt = act["moving_time"]
        is_commute = bool(act.get("commute", False))
        total_distance += dist
        if is_commute:
            commute_distance += dist
        elevation += elev
        moving_time += mt

        gid = act["gear_id"]
        if gid not in gears:
            gears[gid] = {"count": 0, "elevation": 0.0, "distance": 0.0, "moving_time": 0}
        gears[gid]["count"] += 1
        gears[gid]["elevation"] += elev
        gears[gid]["distance"] += dist
        gears[gid]["moving_time"] += mt

        t = "VirtualRide" if is_virtual else "Ride"
        if t not in act_types:
            act_types[t] = {"count": 0, "elevation": 0.0, "distance": 0.0, "moving_time": 0}
        act_types[t]["count"] += 1
        act_types[t]["elevation"] += elev
        act_types[t]["distance"] += dist
        act_types[t]["moving_time"] += mt

    total_km = total_distance / 1000
    virtual_km = act_types.get("VirtualRide", {}).get("distance", 0) / 1000
    virtual_elev = act_types.get("VirtualRide", {}).get("elevation", 0)
    virtual_count = act_types.get("VirtualRide", {}).get("count", 0)

    day_of_year = datetime.datetime.now().timetuple().tm_yday
    diff = total_km - GOAL if full else total_km - (GOAL / 365 * day_of_year)

    bikes = []
    for gid, metrics in gears.items():
        if gid is None:
            continue
        name = _resolve_gear(gid, headers, gear_cache)
        bikes.append({
            "id": gid,
            "name": name,
            "count": metrics["count"],
            "distance_km": round(metrics["distance"] / 1000, 1),
            "elevation_m": round(metrics["elevation"], 0),
            "average_speed": round((metrics["distance"] / 1000) / (metrics["moving_time"] / 3600), 2)
            if metrics["moving_time"] > 0 else 0,
        })

    return {
        "count": count,
        "distance_km": round(total_km, 1),
        "elevation_m": round(elevation, 0),
        "moving_time_s": moving_time,
        "average_speed": round(total_km / (moving_time / 3600), 2) if moving_time > 0 else 0,
        "virtual_km": round(virtual_km, 1),
        "commute_km": round(commute_distance / 1000, 1),
        "virtual_pct": round(virtual_km / total_km * 100, 1) if total_km > 0 else 0,
        "virtual_elev_pct": round(virtual_elev / elevation * 100, 1) if elevation > 0 else 0,
        "virtual_count_pct": round(virtual_count / count * 100, 1) if count > 0 else 0,
        "goal_pct": round(total_km / GOAL * 100, 1),
        "goal_diff_km": round(diff, 0),
        "bikes": bikes,
    }


def _is_current_year(year: int) -> bool:
    return year == datetime.datetime.now().year


def get_ytd_stats() -> list:
    hdrs = _headers()
    gear_cache = _load_gear_cache()
    today = datetime.datetime.today()
    month_day = today.strftime("%m-%d")
    results = []

    for year in range(YEAR_START, today.year + 1):
        current = _is_current_year(year)
        cache_key = f"ytd_{year}"
        cached = _cache_get_ytd(cache_key, current_year=current)
        if cached is not None:
            results.append(cached)
            continue

        try:
            comparison_day = datetime.datetime.strptime(f"{year}-{month_day}", "%Y-%m-%d")
        except ValueError:
            # 29 February compared with a non-leap year.
            comparison_day = datetime.datetime(year, 2, 28)
        end = comparison_day + datetime.timedelta(days=1)
        if current or end > today:
            end = today
        year_activities = _get_year_activities(year, hdrs)
        acts = [activity for activity in year_activities if _activity_start_local(activity) < end]
        summary = _summarise_activities(acts, hdrs, gear_cache, full=False)
        summary["year"] = year
        _cache_set(cache_key, summary)
        results.append(summary)
        time.sleep(0.3)

    return results


def get_yearly_stats() -> list:
    hdrs = _headers()
    gear_cache = _load_gear_cache()
    current_year = datetime.datetime.now().year
    results = []

    for year in range(YEAR_START, current_year + 1):
        current = _is_current_year(year)
        cache_key = f"yearly_{year}"
        cached = _cache_get(cache_key, permanent=not current)
        if cached is not None:
            results.append(cached)
            continue

        acts = _get_year_activities(year, hdrs)
        summary = _summarise_activities(acts, hdrs, gear_cache, full=True)
        summary["year"] = year
        _cache_set(cache_key, summary)
        results.append(summary)
        time.sleep(0.3)

    return results


_QUARTERS = [("01-01", "03-31"), ("04-01", "06-30"), ("07-01", "09-30"), ("10-01", "12-31")]


def _current_quarter() -> int:
    m = datetime.datetime.now().month
    return (m - 1) // 3


def _is_current_quarter(year: int, q_idx: int) -> bool:
    now = datetime.datetime.now()
    return year == now.year and q_idx == _current_quarter()


def get_longchamp_stats() -> dict:
    hdrs = _headers()
    all_segments = []

    for seg_id in LONGCHAMP_SEGMENTS:
        lonlon_day: dict = {}
        record: dict = {}

        for year in range(YEAR_START, datetime.datetime.now().year + 1):
            for q_idx, (q_start, q_end) in enumerate(_QUARTERS):
                current = _is_current_quarter(year, q_idx)
                cache_key = f"longchamp_{seg_id}_{year}_q{q_idx}"
                cached = _cache_get(cache_key, permanent=not current)

                if cached is not None:
                    efforts = cached
                else:
                    data = _get(
                        "https://www.strava.com/api/v3/segment_efforts",
                        {
                            "segment_id": seg_id,
                            "start_date_local": f"{year}-{q_start}",
                            "end_date_local": f"{year}-{q_end}",
                            "per_page": 200,
                        },
                        hdrs,
                    )
                    if not isinstance(data, list):
                        time.sleep(1)
                        continue
                    efforts = data
                    _cache_set(cache_key, efforts)
                    time.sleep(0.3)

                for effort in efforts:
                    if not record or effort["moving_time"] < record["moving_time"]:
                        record = effort
                    day_key = str(effort["start_date_local"])[:10]
                    if day_key not in lonlon_day:
                        lonlon_day[day_key] = {"count": 0, "distance": 0.0, "time": 0}
                    lonlon_day[day_key]["count"] += 1
                    lonlon_day[day_key]["distance"] += float(effort["distance"])
                    lonlon_day[day_key]["time"] += effort["moving_time"]

        sessions = []
        for day, m in lonlon_day.items():
            avg_speed = round((m["distance"] / 1000) / (m["time"] / 3600), 2) if m["time"] > 0 else 0
            sessions.append({
                "day": day,
                "count": m["count"],
                "distance_km": round(m["distance"] / 1000, 2),
                "time_s": m["time"],
                "average_speed": avg_speed,
            })

        sessions_by_speed = sorted(sessions, key=lambda x: x["average_speed"], reverse=True)
        for i, s in enumerate(sessions_by_speed):
            s["rank"] = i + 1

        sessions_by_date = sorted(sessions_by_speed, key=lambda x: x["day"], reverse=True)
        record_avg = round((float(record["distance"]) / 1000) / (record["moving_time"] / 3600), 2) if record else 0

        all_segments.append({
            "segment_id": seg_id,
            "total_sessions": len(sessions),
            "record": {
                "date": str(record.get("start_date_local", ""))[:10] if record else None,
                "time_s": record.get("moving_time") if record else None,
                "average_speed": record_avg,
            },
            "top_by_speed": sessions_by_speed[:TOP],
            "recent": sessions_by_date[:TOP],
            "all_sessions": sessions_by_date,
        })

    return {"segments": all_segments}
