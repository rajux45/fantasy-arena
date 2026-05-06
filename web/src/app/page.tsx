import Link from 'next/link';

import { Nav } from '@/components/Nav';

export default function Home() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-6xl px-4 py-12">
        <section className="grid gap-6 md:grid-cols-2">
          <div className="space-y-5">
            <span className="pill bg-brand-900/60 text-brand-100">Skill-based · 18+ only</span>
            <h1 className="text-4xl font-bold leading-tight md:text-5xl">
              Real fantasy sports + a play-money casino, in one app.
            </h1>
            <p className="text-lg text-slate-300">
              Pick your XI for cricket, football, kabaddi & basketball. Or unwind with provably-fair social
              casino games — virtual coins only. No real-money cash-out, ever.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/auth/signup" className="btn-primary">Get started</Link>
              <Link href="/lobby" className="btn-secondary">Browse contests</Link>
            </div>
            <p className="text-xs text-slate-500">
              Available in most Indian states. Restricted in AS, OD, NL, SK, TG, AP per state law. See{' '}
              <Link href="/legal" className="underline">Legal</Link>.
            </p>
          </div>
          <div className="card grid grid-cols-2 gap-4 text-center">
            {[
              ['🏏', 'Cricket'],
              ['⚽', 'Football'],
              ['🤼', 'Kabaddi'],
              ['🏀', 'Basketball'],
            ].map(([emoji, name]) => (
              <div key={name} className="rounded-xl bg-slate-800/40 p-6">
                <div className="text-4xl">{emoji}</div>
                <div className="mt-2 font-semibold">{name}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-16 grid gap-6 md:grid-cols-3">
          <div className="card">
            <h2 className="text-lg font-semibold">Provably-fair casino</h2>
            <p className="mt-2 text-sm text-slate-300">
              Every round commits a hashed server seed before play. Verify outcomes yourself any time.
            </p>
          </div>
          <div className="card">
            <h2 className="text-lg font-semibold">Double-entry wallet</h2>
            <p className="mt-2 text-sm text-slate-300">
              Three pockets — deposit, winnings, bonus — with full ledger audit trail. GST + TDS handled.
            </p>
          </div>
          <div className="card">
            <h2 className="text-lg font-semibold">Responsible gaming</h2>
            <p className="mt-2 text-sm text-slate-300">
              Self-exclusion, deposit limits, time-spent limits, reality checks — all built in.
            </p>
          </div>
        </section>
      </main>
    </>
  );
}
