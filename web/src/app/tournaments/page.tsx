import Link from 'next/link';

import { Nav } from '@/components/Nav';

const TOURNAMENTS = [
  { id: 't-ipl-26', name: 'IPL 2026', sport: 'cricket', status: 'live', prize_pool: '5 Cr', icon: '🏏' },
  { id: 't-isl-26', name: 'ISL 2026', sport: 'football', status: 'live', prize_pool: '1.5 Cr', icon: '⚽' },
  { id: 't-pkl-26', name: 'PKL 2026', sport: 'kabaddi', status: 'upcoming', prize_pool: '50 L', icon: '🤼' },
  { id: 't-nba-26', name: 'NBA Finals 2026', sport: 'basketball', status: 'upcoming', prize_pool: '25 L', icon: '🏀' },
];

export default function TournamentsPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Tournaments</h1>
        <p className="mt-1 text-sm text-slate-400">Compete across full seasons. Top-100 ranks earn weekly prizes.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {TOURNAMENTS.map((t) => (
            <Link key={t.id} href={`/tournaments/${t.id}`} className="card transition hover:border-brand-700">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-2xl">{t.icon}</div>
                  <div className="mt-2 font-semibold">{t.name}</div>
                  <div className="text-xs uppercase text-slate-500">{t.sport} · {t.status}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400">Prize pool</div>
                  <div className="text-xl font-bold text-brand-400">₹{t.prize_pool}</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}
