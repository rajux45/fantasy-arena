'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

interface Promo { code: string; label: string; pct: number; cap: number; expires: string; active: boolean }
const SAMPLE: Promo[] = [
  { code: 'FIRST100', label: 'First deposit 100%', pct: 100, cap: 200000, expires: '2026-12-31', active: true },
  { code: 'WEEKEND10', label: 'Weekend 10%', pct: 10, cap: 100000, expires: 'rolling', active: true },
];

export default function AdminPromosPage() {
  const [promos, setPromos] = useState<Promo[]>(SAMPLE);
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin · Promo codes</h1>
        <table className="card mt-4 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="pb-2">Code</th><th>Label</th><th className="text-right">% Bonus</th><th className="text-right">Cap</th><th>Expires</th><th></th></tr>
          </thead>
          <tbody>
            {promos.map((p, i) => (
              <tr key={p.code} className="border-t border-slate-800">
                <td className="py-2 font-mono">{p.code}</td>
                <td>{p.label}</td>
                <td className="text-right">{p.pct}%</td>
                <td className="text-right font-mono">₹{(p.cap / 100).toFixed(2)}</td>
                <td>{p.expires}</td>
                <td className="text-right">
                  <button onClick={() => setPromos(promos.map((x, j) => j === i ? { ...x, active: !x.active } : x))} className="btn-secondary text-xs">
                    {p.active ? 'Disable' : 'Enable'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </>
  );
}
