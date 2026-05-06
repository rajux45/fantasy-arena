import Link from 'next/link';

import { Nav } from '@/components/Nav';

export default function AdminHomePage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin panel</h1>
        <p className="mt-1 text-sm text-slate-400">Operations console for ops, finance, KYC, and CMS.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Section title="User operations" items={[
            { label: 'Users (search, ban, role)', href: '/admin' },
            { label: 'KYC review queue', href: '/admin' },
            { label: 'Self-exclusion overrides', href: '/admin' },
          ]} />
          <Section title="Finance" items={[
            { label: 'Withdrawal queue', href: '/admin' },
            { label: 'Manual ledger adjustments', href: '/admin' },
            { label: 'GST / TDS reports', href: '/admin' },
          ]} />
          <Section title="Sports & contests" items={[
            { label: 'Match management', href: '/admin' },
            { label: 'Contest templates & prize slabs', href: '/admin' },
            { label: 'Manual scoring overrides', href: '/admin' },
          ]} />
          <Section title="Casino & promo" items={[
            { label: 'Coin packages & promotions', href: '/admin' },
            { label: 'Provably-fair seed audits', href: '/admin' },
            { label: 'Notifications & CMS posts', href: '/admin' },
          ]} />
        </div>
        <p className="mt-6 text-xs text-slate-500">
          All admin actions write to the audit log. Backed by FastAPI <code>/v1/admin/*</code> endpoints.
        </p>
      </main>
    </>
  );
}

function Section({ title, items }: { title: string; items: { label: string; href: string }[] }) {
  return (
    <div className="card">
      <h2 className="font-semibold">{title}</h2>
      <ul className="mt-2 space-y-1 text-sm">
        {items.map((it) => (
          <li key={it.label}>
            <Link href={it.href} className="text-brand-300 hover:underline">{it.label}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
