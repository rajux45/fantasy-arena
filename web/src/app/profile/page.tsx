'use client';

import Link from 'next/link';

import { Nav } from '@/components/Nav';

export default function ProfilePage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Profile</h1>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {[
            { label: 'Account', items: [
              { name: 'Personal info', href: '/profile' },
              { name: 'Change password', href: '/profile' },
              { name: '2FA / TOTP', href: '/profile' },
            ] },
            { label: 'Verification', items: [
              { name: 'KYC status', href: '/kyc' },
              { name: 'Bank account (for withdrawals)', href: '/wallet' },
            ] },
            { label: 'Wallet', items: [
              { name: 'Balance', href: '/wallet' },
              { name: 'Deposit', href: '/wallet/deposit' },
              { name: 'Withdraw', href: '/wallet/withdraw' },
              { name: 'History', href: '/history' },
            ] },
            { label: 'Activity', items: [
              { name: 'Notifications', href: '/notifications' },
              { name: 'Refer & earn', href: '/referrals' },
              { name: 'Promotions', href: '/promotions' },
            ] },
            { label: 'Safety', items: [
              { name: 'Responsible gaming', href: '/responsible' },
              { name: 'Self-exclude', href: '/responsible' },
              { name: 'Privacy', href: '/privacy' },
            ] },
            { label: 'Help', items: [
              { name: 'Support / FAQ', href: '/support' },
              { name: 'How it works', href: '/how-it-works' },
              { name: 'Provably fair', href: '/provably-fair' },
            ] },
          ].map((sec) => (
            <div key={sec.label} className="card">
              <h2 className="text-sm font-semibold uppercase text-slate-400">{sec.label}</h2>
              <ul className="mt-2 space-y-1 text-sm">
                {sec.items.map((it) => (
                  <li key={it.name}>
                    <Link href={it.href} className="text-slate-200 hover:text-brand-400">→ {it.name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
