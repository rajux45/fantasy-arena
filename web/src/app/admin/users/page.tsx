'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

const SAMPLE = Array.from({ length: 12 }).map((_, i) => ({
  id: `u-${1000 + i}`,
  email: `user${i}@example.com`,
  state: ['MH', 'KA', 'DL', 'TN', 'WB'][i % 5],
  kyc: ['verified', 'pending', 'rejected'][i % 3],
  banned: false,
  joined: '2026-04-12',
  balance: ((10000 + i * 1234) / 100).toFixed(2),
}));

export default function AdminUsersPage() {
  const [filter, setFilter] = useState('');
  const [users, setUsers] = useState(SAMPLE);
  const filtered = users.filter((u) => u.email.includes(filter) || u.id.includes(filter));
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin · Users</h1>
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter by email or id"
          className="mt-3 w-full max-w-md rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
        />
        <table className="card mt-4 w-full text-sm">
          <thead className="text-left text-slate-400">
            <tr>
              <th className="pb-2">ID</th><th>Email</th><th>State</th><th>KYC</th><th>Joined</th><th className="text-right">Balance</th><th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u, i) => (
              <tr key={u.id} className="border-t border-slate-800">
                <td className="py-2 font-mono">{u.id}</td>
                <td>{u.email}</td>
                <td>{u.state}</td>
                <td><span className={`pill ${u.kyc === 'verified' ? 'bg-emerald-900 text-emerald-200' : u.kyc === 'pending' ? 'bg-amber-900 text-amber-200' : 'bg-red-900 text-red-200'}`}>{u.kyc}</span></td>
                <td>{u.joined}</td>
                <td className="text-right font-mono">₹{u.balance}</td>
                <td className="text-right">
                  <button onClick={() => setUsers(users.map((x, j) => i === j ? { ...x, banned: !x.banned } : x))} className="btn-secondary text-xs">
                    {u.banned ? 'Unban' : 'Ban'}
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
