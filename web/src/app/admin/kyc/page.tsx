'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

interface Item { id: string; email: string; pan: string; aadhaar: string; state: string; status: string }
const SAMPLE: Item[] = Array.from({ length: 8 }).map((_, i) => ({
  id: `kyc-${i}`,
  email: `user${i}@example.com`,
  pan: `ABCDE${(1000 + i).toString().slice(-4)}F`,
  aadhaar: `XXXX-XXXX-${(1000 + i).toString().slice(-4)}`,
  state: ['MH', 'KA', 'DL', 'TN'][i % 4],
  status: 'pending',
}));

export default function AdminKycPage() {
  const [items, setItems] = useState<Item[]>(SAMPLE);
  function decide(id: string, s: string) {
    setItems(items.map((it) => it.id === id ? { ...it, status: s } : it));
  }
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin · KYC queue</h1>
        <table className="card mt-4 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="pb-2">ID</th><th>Email</th><th>PAN</th><th>Aadhaar</th><th>State</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id} className="border-t border-slate-800">
                <td className="py-2 font-mono">{it.id}</td>
                <td>{it.email}</td>
                <td className="font-mono">{it.pan}</td>
                <td className="font-mono">{it.aadhaar}</td>
                <td>{it.state}</td>
                <td>{it.status}</td>
                <td className="space-x-2 text-right">
                  <button onClick={() => decide(it.id, 'verified')} className="btn-primary text-xs">Approve</button>
                  <button onClick={() => decide(it.id, 'rejected')} className="btn-secondary text-xs">Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </>
  );
}
