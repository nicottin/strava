import glob
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strava import get_ytd_stats, get_yearly_stats, get_longchamp_stats, CACHE_DIR

app = FastAPI(title="Strava Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "DELETE"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/ytd")
def ytd():
    try:
        return get_ytd_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yearly")
def yearly():
    try:
        return get_yearly_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/longchamp")
def longchamp():
    try:
        return get_longchamp_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache")
def clear_cache():
    removed = []
    for f in glob.glob(os.path.join(CACHE_DIR, "*.json")):
        os.remove(f)
        removed.append(os.path.basename(f))
    return {"cleared": removed}
