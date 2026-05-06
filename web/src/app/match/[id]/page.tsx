'use client';

import { useQuery } from '@tanstack/react-query';
import { formatINR } from '@fantasy-arena/shared/money';
import Link from 'next/link';
import { useParams } from 'next/navigation';

import { Nav } from '@/components/Nav';
import { api } from '@/lib/api';

export default function MatchPage() {
  const params = useParams<{ id: string }>();
  const matchId = params.id;
  const contests = useQuery({
    queryKey: ['contests', matchId],
    queryFn: () => api.matchContests(matchId),
    enabled: !!matchId,
  });
  const players = useQuery({
    queryKey: ['players', matchId],
    queryFn: () => api.matchPlayers(matchId),
    enabled: !!matchId,
  });

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Match · {matchId.slice(0, 8)}</h1>

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <section>
            <h2 className="mb-2 text-lg font-semibold">Contests</h2>
            <div className="space-y-3">
              {contests.data?.map((c) => (
                <div key={c.id} className="card flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{c.name}</div>
                    <div className="text-sm text-slate-400">
                      Prize pool {formatINR(c.prize_pool_paise)} · {c.filled_slots}/{c.total_slots} slots
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold">{formatINR(c.entry_fee_paise)}</div>
                    <Link href={`/match/${matchId}/team-builder`} className="text-sm text-brand-400 hover:underline">
                      Build team →
                    </Link>
                  </div>
                </div>
              )) ?? <p className="text-slate-400">Loading contests…</p>}
            </div>
          </section>
          <section>
            <h2 className="mb-2 text-lg font-semibold">Squads</h2>
            {players.isLoading ? (
              <p className="text-slate-400">Loading players…</p>
            ) : (
              <div className="card grid grid-cols-2 gap-2 text-sm">
                {(players.data ?? []).map((p) => (
                  <div key={p.id} className="flex items-center justify-between rounded-md bg-slate-800/40 px-3 py-2">
                    <span>{p.full_name}</span>
                    <span className="text-slate-400">{p.credits.toFixed(1)}cr</span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </main>
    </>
  );
}
