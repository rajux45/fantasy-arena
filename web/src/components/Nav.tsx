'use client';

import Link from 'next/link';
import { useState } from 'react';

export function Nav() {
  const [moreOpen, setMoreOpen] = useState(false);
  return (
    <nav className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
          <span aria-hidden className="rounded-md bg-brand-600 px-2 py-0.5 text-sm">FA</span>
          Fantasy Arena
        </Link>
        <div className="flex items-center gap-4 text-sm text-slate-300">
          <Link href="/lobby" className="hover:text-white">Lobby</Link>
          <Link href="/casino" className="hover:text-white">Casino</Link>
          <Link href="/tournaments" className="hidden hover:text-white md:inline">Tournaments</Link>
          <Link href="/leaderboard" className="hidden hover:text-white md:inline">Leaderboard</Link>
          <Link href="/wallet" className="hover:text-white">Wallet</Link>
          <div className="relative hidden md:inline">
            <button onClick={() => setMoreOpen((o) => !o)} className="hover:text-white" aria-expanded={moreOpen}>
              More ▾
            </button>
            {moreOpen ? (
              <div className="absolute right-0 mt-2 w-48 rounded-xl border border-slate-800 bg-slate-900 p-2 shadow-xl">
                {[
                  ['/referrals', 'Refer & earn'],
                  ['/promotions', 'Promotions'],
                  ['/notifications', 'Notifications'],
                  ['/history', 'History'],
                  ['/responsible', 'Responsible gaming'],
                  ['/how-it-works', 'How it works'],
                  ['/scoring-rules', 'Scoring rules'],
                  ['/provably-fair', 'Provably fair'],
                  ['/winners', 'Winners'],
                  ['/support', 'Help & support'],
                  ['/legal', 'Legal'],
                ].map(([href, label]) => (
                  <Link key={href} href={href} className="block rounded-md px-2 py-1 text-slate-300 hover:bg-slate-800 hover:text-white">
                    {label}
                  </Link>
                ))}
              </div>
            ) : null}
          </div>
          <Link href="/profile" className="hover:text-white">Profile</Link>
          <Link href="/auth/login" className="btn-primary text-sm">Log in</Link>
        </div>
      </div>
    </nav>
  );
}
