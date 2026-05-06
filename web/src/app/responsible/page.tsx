'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

export default function ResponsibleGamingPage() {
  const [dailyLimit, setDailyLimit] = useState(100000);
  const [sessionMins, setSessionMins] = useState(60);
  const [excludeDays, setExcludeDays] = useState(7);

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Responsible gaming</h1>
        <p className="mt-1 text-sm text-slate-400">
          Set limits to keep play healthy. Limits can be tightened anytime; relaxing requires a 24h cool-off.
        </p>

        <Section title="Deposit limit (per day, paise)">
          <input
            type="number"
            value={dailyLimit}
            onChange={(e) => setDailyLimit(Number(e.target.value))}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
          />
        </Section>

        <Section title="Session-time limit (minutes)">
          <input
            type="number"
            value={sessionMins}
            onChange={(e) => setSessionMins(Number(e.target.value))}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
          />
        </Section>

        <Section title="Self-exclude (days)">
          <select
            value={excludeDays}
            onChange={(e) => setExcludeDays(Number(e.target.value))}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
          >
            <option value={1}>1 day</option>
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={180}>6 months</option>
            <option value={-1}>Permanent</option>
          </select>
        </Section>

        <button className="btn-primary mt-4 w-full">Save limits</button>
      </main>
    </>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card mt-4">
      <h2 className="text-sm text-slate-300">{title}</h2>
      <div className="mt-2">{children}</div>
    </div>
  );
}
