'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

interface Contest { id: string; name: string; sport: string; entry: number; slots: number; prize: number; status: string }
const SAMPLE: Contest[] = [
  { id: 'c1', name: '₹10 Mega', sport: 'cricket', entry: 1000, slots: 500000, prize: 5000000, status: 'open' },
  { id: 'c2', name: 'H2H ₹100', sport: 'cricket', entry: 10000, slots: 2, prize: 19000, status: 'open' },
  { id: 'c3', name: 'Practice', sport: 'football', entry: 0, slots: 1000, prize: 0, status: 'open' },
];

export default function AdminContestsPage() {
  const [contests, setContests] = useState<Contest[]>(SAMPLE);
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin · Contests</h1>
        <button
          className="btn-primary mt-3"
          onClick={() => setContests([...contests, { id: `c${contests.length + 1}`, name: 'New ₹50', sport: 'cricket', entry: 5000, slots: 100, prize: 450000, status: 'draft' }])}
        >
          + New from template
        </button>
        <table className="card mt-4 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="pb-2">ID</th><th>Name</th><th>Sport</th><th className="text-right">Entry</th><th className="text-right">Slots</th><th className="text-right">Prize</th><th>Status</th></tr>
          </thead>
          <tbody>
            {contests.map((c) => (
              <tr key={c.id} className="border-t border-slate-800">
                <td className="py-2 font-mono">{c.id}</td>
                <td>{c.name}</td>
                <td>{c.sport}</td>
                <td className="text-right font-mono">₹{(c.entry / 100).toFixed(2)}</td>
                <td className="text-right font-mono">{c.slots.toLocaleString('en-IN')}</td>
                <td className="text-right font-mono">₹{(c.prize / 100).toFixed(2)}</td>
                <td>{c.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </>
  );
}
