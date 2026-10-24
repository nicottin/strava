# Strava Dashboard

A local web dashboard for your personal Strava stats: year-over-year distance, Longchamp segment history, and bike breakdown.

Built with **FastAPI** (Python) + **React / Vite** (TypeScript).

---

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- A Strava API app (see [Strava developer portal](https://developers.strava.com/docs/authentication/))

---

## First-time setup

### 1. Credentials

Copy the example file and fill in your values:

```bash
cp .credentials_example.properties .credentials.properties
```

| Key | Where to find it |
|---|---|
| `client_id` | [strava.com/settings/api](https://www.strava.com/settings/api) |
| `client_secret` | same page |
| `refresh_token` | run the OAuth flow below |
| `user` / `password` | your Strava login (used by the OAuth flow only) |
| `callback` | the redirect URI registered for your app |

### 2. Get a refresh token (first time only)

Edit `auth.py`, uncomment `print(init_auth())` and comment out the `refresh_token()` call, then run:

```bash
python auth.py
```

Open the printed URL in your browser, authorise the app, copy the `code` from the redirect URL and paste it when prompted. The response JSON contains `refresh_token` — paste it into `.credentials.properties`. Then revert `auth.py`.

### 3. Configuration

Edit `config.properties` to set your annual distance goal, the first year to include, and how many top sessions to display:

```ini
[CONFIG]
goal = 5000        # km per year
year_start = 2016
top = 10
```

---

## Running the dashboard

```bash
./start.sh
```

This single command:
1. Synchronises Python dependencies from `pyproject.toml` / `uv.lock`
2. Installs / updates Node dependencies (`ui/package.json`)
3. Starts the FastAPI backend on `http://localhost:8000`
4. Starts the Vite dev server on `http://localhost:5173` and opens it in your browser

Press **Ctrl+C** to stop both servers.

---

## How caching works

The dashboard caches the activity list for each year. Past years are then filtered locally for YTD comparisons. For the current year, only a three-day overlap is fetched after the first synchronisation, so recent edits are picked up without downloading the full year again. Segment efforts use a separate quarterly cache.

| Cache file | Content | Expires |
|---|---|---|
| `activities_<year>.json` | Activity list and last synchronisation point | Past years: **never**; current year: incremental refresh after **1 hour** |
| `ytd_<year>.json` | YTD activity summary for a past year | **Until the next day**, then recomputed from the local activity list |
| `ytd_<current_year>.json` | YTD activity summary for the current year | **1 hour** |
| `yearly_<year>.json` | Full-year activity summary for a past year | **Never** |
| `yearly_<current_year>.json` | Full-year summary for the current year | **1 hour** |
| `longchamp_<seg>_<year>_q<n>.json` | Segment efforts for a past quarter | **Never** |
| `longchamp_<seg>_<year>_q<current>.json` | Efforts for the current quarter | **1 hour** |
| `gear_names.json` | Bike names resolved from gear IDs | **Never** |

The cache directory (`api/.cache/`) is excluded from git.

**Force a full refresh** (e.g. after adding past activities or changing the segment list):

```bash
curl -X DELETE http://localhost:8000/api/cache
```

Then reload the page — the next request will re-fetch everything from Strava.

---

## Project structure

```
strava/
├── pyproject.toml        # Python project and dependencies (uv)
├── uv.lock               # Locked Python dependency versions
├── api/
│   ├── main.py          # FastAPI app — 3 endpoints + cache-clear
│   └── strava.py        # Strava API calls & caching logic
├── ui/
│   └── src/
│       ├── App.tsx
│       ├── api.ts                       # typed fetch helpers
│       └── components/
│           ├── YearOverYear.tsx         # distance bar chart
│           ├── LongchampTrend.tsx       # speed trend line chart
│           ├── LongchampTop.tsx         # top / recent sessions table
│           └── BikeBreakdown.tsx        # per-bike breakdown
├── auth.py              # OAuth helper
├── config.properties    # goal, year_start, top
├── start.sh             # one-command launcher
└── .credentials.properties  # secrets — never committed
```

---

## Links

- [Strava API documentation](https://developers.strava.com/docs/reference/)
- [Strava authentication guide](https://developers.strava.com/docs/authentication/)
