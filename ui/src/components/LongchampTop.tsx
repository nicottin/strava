import { useState } from 'react';
import type { LongchampSession, LongchampSegment } from '../api';

interface Props { segment: LongchampSegment }

function fmtTime(s: number) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${String(sec).padStart(2, '0')}`;
}

type Tab = 'speed' | 'recent';

export default function LongchampTop({ segment }: Props) {
  const [tab, setTab] = useState<Tab>('speed');
  const label = segment.segment_id === 3572501 ? 'Longchamp (regular)' : 'Longchamp (long)';
  const rows: LongchampSession[] = tab === 'speed' ? segment.top_by_speed : segment.recent;

  return (
    <div className="bg-gray-800 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-white">{label} — Sessions</h2>
        <div className="flex gap-1 text-xs">
          {(['speed', 'recent'] as Tab[]).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1 rounded-full transition-colors ${
                tab === t ? 'bg-orange-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {t === 'speed' ? 'Top speed' : 'Recent'}
            </button>
          ))}
        </div>
      </div>

      {segment.record.date && (
        <div className="mb-3 bg-orange-500/10 border border-orange-500/30 rounded-xl px-4 py-2 text-sm">
          <span className="text-orange-400 font-semibold">Record</span>
          <span className="text-gray-300 ml-2">
            {fmtTime(segment.record.time_s!)} · {segment.record.average_speed} km/h · {segment.record.date}
          </span>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 text-xs border-b border-gray-700">
              <th className="text-left py-2 pr-3">#</th>
              <th className="text-left py-2 pr-3">Date</th>
              <th className="text-right py-2 pr-3">Laps</th>
              <th className="text-right py-2 pr-3">Speed</th>
              <th className="text-right py-2">Rank</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={r.day} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                <td className="py-2 pr-3 text-gray-400">{i + 1}</td>
                <td className="py-2 pr-3 text-white font-medium">{r.day}</td>
                <td className="py-2 pr-3 text-gray-300 text-right">{r.count}</td>
                <td className="py-2 pr-3 text-orange-400 text-right font-semibold">{r.average_speed} km/h</td>
                <td className="py-2 text-gray-400 text-right">{r.rank}/{segment.total_sessions}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-gray-500">{segment.total_sessions} total sessions</p>
    </div>
  );
}
