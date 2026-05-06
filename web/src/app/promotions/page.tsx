import { Nav } from '@/components/Nav';

const PROMOS = [
  { code: 'FIRST100', label: 'First deposit', detail: '100% bonus on your first ₹500–₹2000 deposit.', expires: '2026-12-31' },
  { code: 'WEEKEND10', label: 'Weekend boost', detail: '10% extra on every weekend deposit.', expires: 'rolling' },
  { code: 'COIN50', label: 'Casino coins bonus', detail: '50% extra coins on any pack purchase.', expires: 'rolling' },
  { code: 'SPECIAL26', label: 'Republic Day', detail: 'Mega contest with ₹26 lakh prize pool.', expires: '2026-01-26' },
];

export default function PromotionsPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Promotions</h1>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {PROMOS.map((p) => (
            <div key={p.code} className="card">
              <div className="flex items-center justify-between">
                <span className="pill bg-brand-900 text-brand-100">{p.label}</span>
                <span className="font-mono text-xs text-slate-400">code {p.code}</span>
              </div>
              <p className="mt-3 text-slate-300">{p.detail}</p>
              <div className="mt-2 text-xs text-slate-500">Expires: {p.expires}</div>
            </div>
          ))}
        </div>
        <p className="mt-6 text-xs text-slate-500">
          T&Cs apply. Bonus credits live in the bonus pocket and can&apos;t be withdrawn directly; they
          convert to winnings as you play eligible contests.
        </p>
      </main>
    </>
  );
}
