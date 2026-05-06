'use client';

import { useParams } from 'next/navigation';

import { Nav } from '@/components/Nav';

export default function TournamentDetailPage() {
  const params = useParams<{ id: string }>();
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-semibold">{params.id}</h1>
        <p className="mt-1 text-sm text-slate-400">Full-season standings, weekly leaderboards, and signup contests.</p>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="card">
            <div className="text-xs uppercase text-slate-500">Total prize pool</div>
            <div className="mt-1 text-3xl font-bold text-brand-400">₹5 Cr</div>
          </div>
          <div className="card">
            <div className="text-xs uppercase text-slate-500">Players joined</div>
            <div className="mt-1 text-3xl font-bold">12,48,302</div>
          </div>
          <div className="card">
            <div className="text-xs uppercase text-slate-500">Matches done</div>
            <div className="mt-1 text-3xl font-bold">22 / 74</div>
          </div>
        </div>

        <h2 className="mt-8 text-lg font-semibold">Top 10 (live)</h2>
        <table className="card mt-3 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr>
              <th className="pb-2">#</th>
              <th>Player</th>
              <th className="text-right">Points</th>
              <th className="text-right">Prize so far</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 10 }).map((_, i) => (
              <tr key={i} className="border-t border-slate-800">
                <td className="py-2 font-mono">{i + 1}</td>
                <td>Player_{(i + 1).toString().padStart(3, '0')}</td>
                <td className="text-right font-mono">{(15000 - i * 35).toFixed(1)}</td>
                <td className="text-right font-mono">₹{((20 - i * 1.5) * 100000).toLocaleString('en-IN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </>
  );
}
