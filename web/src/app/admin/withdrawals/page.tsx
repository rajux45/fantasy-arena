'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

const SAMPLE = Array.from({ length: 8 }).map((_, i) => ({
  id: `wd-${i}`,
  user: `user${i}@example.com`,
  gross: 5000 + i * 1000,
  tds: Math.round((5000 + i * 1000) * 0.3),
  net: Math.round((5000 + i * 1000) * 0.7),
  status: 'pending',
}));

export default function AdminWithdrawalsPage() {
  const [items, setItems] = useState(SAMPLE);
  function set(id: string, s: string) {
    setItems(items.map((x) => x.id === id ? { ...x, status: s } : x));
  }
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin · Withdrawals</h1>
        <table className="card mt-4 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="pb-2">ID</th><th>User</th><th className="text-right">Gross</th><th className="text-right">TDS 30%</th><th className="text-right">Net</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id} className="border-t border-slate-800">
                <td className="py-2 font-mono">{it.id}</td>
                <td>{it.user}</td>
                <td className="text-right font-mono">₹{it.gross}</td>
                <td className="text-right font-mono text-amber-300">₹{it.tds}</td>
                <td className="text-right font-mono">₹{it.net}</td>
                <td>{it.status}</td>
                <td className="space-x-2 text-right">
                  <button onClick={() => set(it.id, 'approved')} className="btn-primary text-xs">Approve</button>
                  <button onClick={() => set(it.id, 'rejected')} className="btn-secondary text-xs">Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </>
  );
}
