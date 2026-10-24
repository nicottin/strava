import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell,
} from 'recharts';
import type { YearStat } from '../api';

interface Props { data: YearStat[]; currentYear: number }

const GOAL = 5000;

const LEGEND = [
  { color: '#22c55e', label: 'Total km (goal met)' },
  { color: '#fc4c02', label: 'Total km (goal missed)' },
  { color: '#f97316', label: 'Virtual km' },
  { color: '#6366f1', label: 'Commute km' },
];

export default function FullYear({ data, currentYear }: Props) {
  const sorted = [...data]
    .filter(d => d.year < currentYear)
    .sort((a, b) => a.year - b.year);

  return (
    <div className="bg-gray-800 rounded-2xl p-5">
      <h2 className="text-lg font-semibold text-white mb-1">Distance — Full Year</h2>
      <p className="text-xs text-gray-500 mb-4">Completed years only · current year excluded</p>

      <div className="flex flex-wrap gap-4 mb-4">
        {LEGEND.map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm flex-shrink-0" style={{ background: color }} />
            <span className="text-xs text-gray-400">{label}</span>
          </div>
        ))}
      </div>

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
          <ReferenceLine
            y={GOAL}
            stroke="#6b7280"
            strokeDasharray="4 2"
            label={{ value: 'Goal', fill: '#6b7280', fontSize: 11 }}
          />
          <Bar dataKey="distance_km" name="Total km" radius={[4, 4, 0, 0]} legendType="none">
            {sorted.map(d => (
              <Cell key={d.year} fill={d.distance_km >= GOAL ? '#22c55e' : '#fc4c02'} />
            ))}
          </Bar>
          <Bar dataKey="virtual_km" name="Virtual km" fill="#f97316" radius={[4, 4, 0, 0]} opacity={0.6} legendType="none" />
          <Bar dataKey="commute_km" name="Commute km" fill="#6366f1" radius={[4, 4, 0, 0]} opacity={0.8} legendType="none" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
