import Link from 'next/link';

import { CASINO_GAMES } from '@fantasy-arena/shared/casino';
import { Nav } from '@/components/Nav';

export default function CasinoLobbyPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Social casino</h1>
        <p className="mt-2 text-sm text-slate-300">
          All games are play-money only. Coins are virtual; <strong className="text-white">no real-money cash-out</strong>.
        </p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Object.values(CASINO_GAMES).map((g) => (
            <Link key={g.slug} href={`/casino/${g.slug}`} className="card transition hover:border-brand-700">
              <div className="font-semibold capitalize">{g.name}</div>
              <p className="mt-1 text-sm text-slate-400">{g.description}</p>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}
