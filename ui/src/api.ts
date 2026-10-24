export interface YearStat {
  year: number;
  count: number;
  distance_km: number;
  elevation_m: number;
  moving_time_s: number;
  average_speed: number;
  virtual_km: number;
  commute_km: number;
  virtual_pct: number;
  virtual_elev_pct: number;
  virtual_count_pct: number;
  goal_pct: number;
  goal_diff_km: number;
  bikes: BikeStat[];
}

export interface BikeStat {
  id: string;
  name: string;
  count: number;
  distance_km: number;
  elevation_m: number;
  average_speed: number;
}

export interface LongchampSession {
  day: string;
  count: number;
  distance_km: number;
  time_s: number;
  average_speed: number;
  rank: number;
}

export interface LongchampSegment {
  segment_id: number;
  total_sessions: number;
  record: {
    date: string | null;
    time_s: number | null;
    average_speed: number;
  };
  top_by_speed: LongchampSession[];
  recent: LongchampSession[];
  all_sessions: LongchampSession[];
}

export interface LongchampData {
  segments: LongchampSegment[];
}

export async function fetchYtd(): Promise<YearStat[]> {
  const r = await fetch('/api/ytd');
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchYearly(): Promise<YearStat[]> {
  const r = await fetch('/api/yearly');
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchLongchamp(): Promise<LongchampData> {
  const r = await fetch('/api/longchamp');
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
