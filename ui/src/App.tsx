import { useEffect, useState } from 'react';
import { fetchYtd, fetchYearly, fetchLongchamp } from './api';
import type { YearStat, LongchampData } from './api';
import YearOverYear from './components/YearOverYear';
import FullYear from './components/FullYear';
import LongchampTrend from './components/LongchampTrend';
import LongchampTop from './components/LongchampTop';
import BikeBreakdown from './components/BikeBreakdown';

function Spinner() {
  return (
    <div className="flex items-center justify-center h-40">
      <div className="w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

function ErrorBox({ msg }: { msg: string }) {
  return (
    <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-4 text-red-300 text-sm">
      {msg}
    </div>
  );
}

export default function App() {
  const currentYear = new Date().getFullYear();

  const [ytd, setYtd] = useState<YearStat[] | null>(null);
  const [ytdError, setYtdError] = useState<string | null>(null);

  const [yearly, setYearly] = useState<YearStat[] | null>(null);
  const [yearlyError, setYearlyError] = useState<string | null>(null);

  const [longchamp, setLongchamp] = useState<LongchampData | null>(null);
  const [longchampError, setLongchampError] = useState<string | null>(null);

  useEffect(() => {
    fetchYtd()
      .then(data => { setYtd(data); return fetchYearly(); })
      .then(setYearly)
      .catch(e => {
        const msg = String(e);
        if (!ytd) setYtdError(msg); else setYearlyError(msg);
      });
  }, []);

  useEffect(() => {
    fetchLongchamp()
      .then(setLongchamp)
      .catch(e => setLongchampError(String(e)));
  }, []);

  const currentYearBikes = ytd?.find(d => d.year === currentYear)?.bikes ?? [];

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: '#fc4c02' }}>
          <svg viewBox="0 0 24 24" className="w-5 h-5 fill-white">
            <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169" />
          </svg>
        </div>
        <h1 className="text-xl font-bold text-white">Strava Dashboard</h1>
        <span className="ml-auto text-xs text-gray-500">Live data</span>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        {/* Year-over-year */}
        {ytdError ? (
          <ErrorBox msg={`YTD stats: ${ytdError}`} />
        ) : !ytd ? (
          <div className="bg-gray-800 rounded-2xl p-5">
            <p className="text-sm text-gray-400 mb-3">Loading year-over-year stats…</p>
            <Spinner />
          </div>
        ) : (
          <YearOverYear data={ytd} currentYear={currentYear} />
        )}

        {/* Full year */}
        {yearlyError ? (
          <ErrorBox msg={`Yearly stats: ${yearlyError}`} />
        ) : !yearly ? (
          <div className="bg-gray-800 rounded-2xl p-5">
            <p className="text-sm text-gray-400 mb-3">Loading full-year stats…</p>
            <Spinner />
          </div>
        ) : (
          <FullYear data={yearly} currentYear={currentYear} />
        )}

        {/* Bike breakdown */}
        {ytd && currentYearBikes.length > 0 && (
          <BikeBreakdown bikes={currentYearBikes} />
        )}

        {/* Longchamp */}
        {longchampError ? (
          <ErrorBox msg={`Longchamp: ${longchampError}`} />
        ) : !longchamp ? (
          <div className="bg-gray-800 rounded-2xl p-5">
            <p className="text-sm text-gray-400 mb-3">Loading Longchamp segment data…</p>
            <Spinner />
          </div>
        ) : (
          longchamp.segments.map(seg => (
            <div key={seg.segment_id} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LongchampTrend sessions={seg.all_sessions} segmentId={seg.segment_id} />
              <LongchampTop segment={seg} />
            </div>
          ))
        )}
      </main>
    </div>
  );
}
