'use client';

import { formatINR } from '@fantasy-arena/shared/money';
import { useState } from 'react';

import { Nav } from '@/components/Nav';

const PRESETS = [10000, 50000, 100000, 500000]; // paise

export default function DepositPage() {
  const [amount, setAmount] = useState(50000);
  const [busy, setBusy] = useState(false);
  const [info, setInfo] = useState<string | null>(null);

  // GST inclusive: 28% on 21.87% of total. Approximate split for display only.
  const gstPaise = Math.round(amount * 0.2187);
  const playablePaise = amount - gstPaise;

  async function handlePay() {
    setBusy(true);
    setInfo(null);
    try {
      // In production this would call POST /v1/wallet/deposits → Razorpay order.
      await new Promise((r) => setTimeout(r, 600));
      setInfo(`Sandbox order created for ${formatINR(amount)} (GST ${formatINR(gstPaise)} inclusive).`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-md px-4 py-8">
        <h1 className="text-2xl font-semibold">Deposit</h1>
        <p className="mt-1 text-sm text-slate-400">Add funds via UPI / netbanking / card (Razorpay).</p>

        <div className="card mt-6">
          <div className="mb-3 flex flex-wrap gap-2">
            {PRESETS.map((p) => (
              <button
                key={p}
                onClick={() => setAmount(p)}
                className={`pill ${amount === p ? 'bg-brand-600 text-white' : 'bg-slate-800 text-slate-300'}`}
              >
                {formatINR(p)}
              </button>
            ))}
          </div>
          <label className="block">
            <span className="text-sm text-slate-300">Amount (paise)</span>
            <input
              type="number"
              min={5000}
              max={100_00_000}
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>

          <ul className="mt-4 text-sm text-slate-300">
            <li>You pay: <span className="font-mono">{formatINR(amount)}</span></li>
            <li>GST 28% (inclusive): <span className="font-mono">{formatINR(gstPaise)}</span></li>
            <li>Playable balance: <span className="font-mono">{formatINR(playablePaise)}</span></li>
          </ul>

          <button onClick={handlePay} disabled={busy} className="btn-primary mt-4 w-full disabled:opacity-50">
            {busy ? 'Creating order…' : 'Pay via Razorpay'}
          </button>
          {info ? <p className="mt-3 text-sm text-emerald-400">{info}</p> : null}
        </div>

        <p className="mt-4 text-xs text-slate-500">
          By depositing you confirm you are 18+, KYC-verified, and not in a state restricted from real-money
          fantasy. All amounts are in paise (₹1 = 100 paise).
        </p>
      </main>
    </>
  );
}
