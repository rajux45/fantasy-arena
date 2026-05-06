'use client';

import { formatINR } from '@fantasy-arena/shared/money';
import { useState } from 'react';

import { Nav } from '@/components/Nav';

interface Entry {
  rank: number;
  name: string;
  team: string;
  points: number;
  prize_paise: number;
}

const SAMPLE: Entry[] = [
  { rank: 1, name: 'Rohit M.', team: 'RM_XI', points: 624.5, prize_paise: 5_00_00_000 },
  { rank: 2, name: 'Aakash S.', team: 'AS_Lions', points: 621.0, prize_paise: 1_50_00_000 },
  { rank: 3, name: 'Priya N.', team: 'PN_Power', points: 615.5, prize_paise: 75_00_000 },
  { rank: 4, name: 'Devansh K.', team: 'DK_Slammers', points: 610.0, prize_paise: 25_00_000 },
  { rank: 5, name: 'Ishita R.', team: 'IR_Strikers', points: 605.5, prize_paise: 10_00_000 },
];

export default function LeaderboardPage() {
  const [tick, setTick] = useState(0);
  // Demo: simulate "live" updates every 3s.
  if (typeof window !== 'undefined') {
    setTimeout(() => setTick((t) => t + 1), 3000);
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Live leaderboard <span className="text-xs text-slate-400">tick {tick}</span></h1>

        <table className="card mt-6 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr>
              <th className="pb-2">Rank</th>
              <th>Player</th>
              <th>Team</th>
              <th className="text-right">Points</th>
              <th className="text-right">Prize</th>
            </tr>
          </thead>
          <tbody>
            {SAMPLE.map((e) => (
              <tr key={e.rank} className="border-t border-slate-800">
                <td className="py-2 font-mono">#{e.rank}</td>
                <td>{e.name}</td>
                <td className="text-slate-400">{e.team}</td>
                <td className="text-right font-mono">{e.points.toFixed(1)}</td>
                <td className="text-right font-mono">{formatINR(e.prize_paise)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-3 text-xs text-slate-500">
          In production this updates via WebSocket from <code>/v1/ws/leaderboard?contest_id=…</code>.
        </p>
      </main>
    </>
  );
}
