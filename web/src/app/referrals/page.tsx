'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

export default function ReferralsPage() {
  const code = 'FA-RAJU-A1B2';
  const link = `https://fantasy-arena.in/r/${code}`;
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Refer & earn</h1>
        <p className="mt-1 text-sm text-slate-400">
          Refer a friend. They get ₹50 bonus on first deposit. You get ₹100 cashback after their first contest.
        </p>

        <div className="card mt-6">
          <div className="text-xs uppercase text-slate-500">Your referral code</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="font-mono text-2xl">{code}</span>
            <button onClick={copy} className="btn-secondary">
              {copied ? 'Copied!' : 'Copy link'}
            </button>
          </div>
          <div className="mt-3 break-all rounded-lg bg-slate-800/50 p-3 font-mono text-sm">{link}</div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <Stat label="Referrals" value="0" />
          <Stat label="Activated (joined contest)" value="0" />
          <Stat label="Total earned" value="₹0" />
        </div>

        <h2 className="mt-8 text-lg font-semibold">How it works</h2>
        <ol className="mt-2 list-inside list-decimal space-y-1 text-sm text-slate-300">
          <li>Share your code or link with a friend.</li>
          <li>They sign up using your code.</li>
          <li>They get ₹50 deposit bonus, you get ₹100 cashback after their first paid contest.</li>
          <li>No limit on number of referrals.</li>
        </ol>
        <p className="mt-3 text-xs text-slate-500">
          Cashback is credited to your bonus pocket; bonus pocket plays only (cannot be withdrawn).
        </p>
      </main>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card">
      <div className="text-xs text-slate-400">{label}</div>
      <div className="mt-1 text-3xl font-bold">{value}</div>
    </div>
  );
}
