'use client';

import { formatINR } from '@fantasy-arena/shared/money';
import { useState } from 'react';

import { Nav } from '@/components/Nav';

export default function WithdrawPage() {
  const [amount, setAmount] = useState(100000); // paise
  const [acct, setAcct] = useState('');
  const [ifsc, setIfsc] = useState('');
  const [busy, setBusy] = useState(false);
  const [out, setOut] = useState<string | null>(null);

  // 30% TDS on net winnings (Sec 194BA), approximate display.
  const tds = Math.round(amount * 0.3);
  const payout = amount - tds;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setOut(null);
    try {
      await new Promise((r) => setTimeout(r, 600));
      setOut(
        `Withdrawal of ${formatINR(amount)} requested. After TDS ${formatINR(tds)}, you'll receive ${formatINR(payout)} to ${acct}/${ifsc}.`,
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-md px-4 py-8">
        <h1 className="text-2xl font-semibold">Withdraw winnings</h1>
        <p className="mt-1 text-sm text-slate-400">
          Only winnings are withdrawable. KYC required. TDS at 30% deducted at source (Sec 194BA).
        </p>

        <form onSubmit={handleSubmit} className="card mt-6 space-y-3">
          <label className="block">
            <span className="text-sm text-slate-300">Amount (paise)</span>
            <input
              type="number"
              min={10000}
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">Bank account #</span>
            <input
              required
              value={acct}
              onChange={(e) => setAcct(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">IFSC</span>
            <input
              required
              value={ifsc}
              onChange={(e) => setIfsc(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>

          <ul className="text-sm text-slate-300">
            <li>Gross: <span className="font-mono">{formatINR(amount)}</span></li>
            <li>TDS 30%: <span className="font-mono">−{formatINR(tds)}</span></li>
            <li>You receive: <span className="font-mono">{formatINR(payout)}</span></li>
          </ul>

          <button type="submit" disabled={busy} className="btn-primary w-full disabled:opacity-50">
            {busy ? 'Submitting…' : 'Request withdrawal'}
          </button>
          {out ? <p className="text-sm text-emerald-400">{out}</p> : null}
        </form>
      </main>
    </>
  );
}
