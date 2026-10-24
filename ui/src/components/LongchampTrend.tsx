import { useState, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import type { LongchampSession } from '../api';

interface Props { sessions: LongchampSession[]; segmentId: number }

const WINDOWS = [
  { label: '3 months', months: 3 },
  { label: '6 months', months: 6 },
  { label: '12 months', months: 12 },
  { label: 'All time', months: 0 },
];

export default function LongchampTrend({ sessions, segmentId }: Props) {
  const [months, setMonths] = useState(12);
  const label = segmentId === 3572501 ? 'Longchamp (regular)' : 'Longchamp (long)';

  const filtered = useMemo(() => {
    const all = [...sessions].sort((a, b) => a.day.localeCompare(b.day));
    if (months === 0) return all;
    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - months);
    const cutoffStr = cutoff.toISOString().slice(0, 10);
    return all.filter(s => s.day >= cutoffStr);
  }, [sessions, months]);

  return (
    <div className="bg-gray-800 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">{label} — Speed Trend</h2>
        <div className="flex gap-1 text-xs">
          {WINDOWS.map(w => (
            <button
              key={w.months}
              onClick={() => setMonths(w.months)}
              className={`px-3 py-1 rounded-full transition-colors ${
                months === w.months ? 'bg-orange-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {w.label}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={filtered} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="day" tick={{ fill: '#9ca3af', fontSize: 10 }} interval="preserveStartEnd" />
          <YAxis
            domain={['auto', 'auto']}
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            unit=" km/h"
            width={72}
          />
          <Tooltip
            contentStyle={{ background: '#1f2937', border: 'none', borderRadius: 8 }}
            labelStyle={{ color: '#f9fafb' }}
            formatter={(v: number, name: string) => [`${v} km/h`, name]}
          />
          <Line
            type="monotone"
            dataKey="average_speed"
            name="Avg speed"
            stroke="#fc4c02"
            dot={filtered.length < 30}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="mt-3 text-xs text-gray-400 text-center">
        {filtered.length} sessions · hover for details
      </p>
    </div>
  );
}
