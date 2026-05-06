'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

export default function HistoryPage() {
  const [tab, setTab] = useState<'fantasy' | 'casino' | 'wallet'>('fantasy');
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-semibold">History</h1>
        <div className="mt-4 flex gap-2 text-sm">
          {([
            ['fantasy', 'Fantasy contests'],
            ['casino', 'Casino rounds'],
            ['wallet', 'Wallet ledger'],
          ] as const).map(([k, l]) => (
            <button
              key={k}
              onClick={() => setTab(k)}
              className={`pill ${tab === k ? 'bg-brand-600 text-white' : 'bg-slate-800 text-slate-300'}`}
            >
              {l}
            </button>
          ))}
        </div>

        <div className="card mt-6 text-sm">
          {tab === 'fantasy' ? (
            <Table headers={['Match', 'Contest', 'Rank', 'Prize']} rows={[
              ['MI vs CSK', '₹10 Mega', '14,512 / 5,00,000', '₹0'],
              ['RCB vs KKR', '₹100 H2H', '1 / 2', '₹190'],
              ['IND vs AUS', 'Practice', '52 / 1,000', '—'],
            ]} />
          ) : tab === 'casino' ? (
            <Table headers={['Game', 'Bet', 'Multiplier', 'Payout']} rows={[
              ['Crash', '100c', '2.34x', '234c'],
              ['Dice (over 50.5)', '100c', '0.00x', '0c'],
              ['Plinko 12-row', '50c', '1.50x', '75c'],
            ]} />
          ) : (
            <Table headers={['Time', 'Kind', 'Account', 'Amount']} rows={[
              ['10:14am', 'deposit.credit', 'wallet:deposit', '+₹200'],
              ['10:18am', 'contest.fee', 'wallet:deposit', '−₹10'],
              ['10:20am', 'contest.payout', 'wallet:winnings', '+₹190'],
            ]} />
          )}
        </div>
      </main>
    </>
  );
}

function Table({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <table className="w-full">
      <thead className="text-left text-slate-400">
        <tr>{headers.map((h) => <th key={h} className="pb-2">{h}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i} className="border-t border-slate-800">
            {r.map((c, j) => <td key={j} className="py-2">{c}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
