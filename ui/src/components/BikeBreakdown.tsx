import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import type { BikeStat } from '../api';

interface Props { bikes: BikeStat[] }

const COLORS = ['#fc4c02', '#f97316', '#fb923c', '#fdba74'];

export default function BikeBreakdown({ bikes }: Props) {
  const sorted = [...bikes].sort((a, b) => b.distance_km - a.distance_km);

  return (
    <div className="bg-gray-800 rounded-2xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Bike Breakdown (current year)</h2>
      {sorted.length === 0 ? (
        <p className="text-gray-400 text-sm text-center py-8">Only one bike this year — no breakdown needed.</p>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sorted} layout="vertical" margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} unit=" km" />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                width={120}
              />
              <Tooltip
                contentStyle={{ background: '#1f2937', border: 'none', borderRadius: 8 }}
                formatter={(v: number) => [`${v} km`, 'Distance']}
              />
              <Bar dataKey="distance_km" radius={[0, 4, 4, 0]}>
                {sorted.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {sorted.map((b, i) => (
              <div key={b.id} className="bg-gray-700 rounded-xl p-3 flex items-start gap-2">
                <span
                  className="w-3 h-3 mt-1 rounded-sm flex-shrink-0"
                  style={{ background: COLORS[i % COLORS.length] }}
                />
                <div>
                  <p className="text-white text-sm font-medium">{b.name}</p>
                  <p className="text-gray-400 text-xs">{b.distance_km} km · {b.elevation_m.toLocaleString()} m</p>
                  <p className="text-gray-400 text-xs">{b.count} rides · {b.average_speed} km/h avg</p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
