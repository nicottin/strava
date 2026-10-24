import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import type { YearStat } from '../api';

interface Props { data: YearStat[]; currentYear: number }

export default function YearOverYear({ data, currentYear }: Props) {
  const sorted = [...data].sort((a, b) => a.year - b.year);
  return (
    <div className="bg-gray-800 rounded-2xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Distance — Year over Year (YTD)</h2>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={sorted} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="year" tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} unit=" km" width={64} />
          <Tooltip
            contentStyle={{ background: '#1f2937', border: 'none', borderRadius: 8 }}
            labelStyle={{ color: '#f9fafb' }}
            formatter={(v: number, name: string) => [`${v} km`, name]}
          />
          <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
          {sorted.map(d => d.year).map(year => (
            year === currentYear
              ? <ReferenceLine key={year} x={year} stroke="#fc4c02" strokeDasharray="4 2" />
              : null
          ))}
          <Bar dataKey="distance_km" name="Total km" fill="#fc4c02" radius={[4, 4, 0, 0]} />
          <Bar dataKey="virtual_km" name="Virtual km" fill="#f97316" radius={[4, 4, 0, 0]} opacity={0.6} />
          <Bar dataKey="commute_km" name="Commute km" fill="#6366f1" radius={[4, 4, 0, 0]} opacity={0.8} />
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        {sorted.filter(d => d.year >= currentYear - 2).map(d => (
          <div key={d.year} className="bg-gray-700 rounded-xl p-3">
            <p className="text-xs text-gray-400 mb-1">{d.year}</p>
            <p className="text-xl font-bold text-white">{d.distance_km.toLocaleString()} km</p>
            <p className="text-xs text-gray-400">{d.count} rides · {d.elevation_m.toLocaleString()} m</p>
            <p className={`text-xs mt-1 font-medium ${d.goal_diff_km >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              Goal {d.goal_pct}% ({d.goal_diff_km >= 0 ? '+' : ''}{d.goal_diff_km} km)
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
