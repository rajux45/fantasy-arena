'use client';

import { useQuery } from '@tanstack/react-query';
import { listSports, type SportSlug } from '@fantasy-arena/shared/sports';
import Link from 'next/link';
import { useState } from 'react';

import { Nav } from '@/components/Nav';
import { api } from '@/lib/api';

export default function LobbyPage() {
  const [sport, setSport] = useState<SportSlug>('cricket');
  const matches = useQuery({
    queryKey: ['matches', sport],
    queryFn: () => api.listMatches(sport),
  });

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Lobby</h1>

        <div className="mt-4 flex flex-wrap gap-2">
          {listSports().map((s) => (
            <button
              key={s.slug}
              onClick={() => setSport(s.slug)}
              className={`pill ${sport === s.slug ? 'bg-brand-600 text-white' : 'bg-slate-800 text-slate-300'}`}
            >
              {s.emoji} {s.name}
            </button>
          ))}
        </div>

        <section className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {matches.isLoading ? (
            <p className="text-slate-400">Loading matches…</p>
          ) : matches.error ? (
            <p className="text-red-400">Couldn&apos;t load matches. Is the API running?</p>
          ) : matches.data && matches.data.length > 0 ? (
            matches.data.map((m) => (
              <Link key={m.id} href={`/match/${m.id}`} className="card transition hover:border-brand-700">
                <div className="text-xs uppercase tracking-wide text-slate-500">{m.sport}</div>
                <div className="mt-1 text-lg font-semibold">{m.home_team} vs {m.away_team}</div>
                <div className="mt-1 text-sm text-slate-400">{m.venue ?? '—'}</div>
                <div className="mt-2 text-sm text-slate-300">
                  Starts {new Date(m.starts_at).toLocaleString('en-IN')}
                </div>
              </Link>
            ))
          ) : (
            <p className="text-slate-400">No matches yet for this sport.</p>
          )}
        </section>
      </main>
    </>
  );
}
