'use client';

import { useQuery } from '@tanstack/react-query';
import { listSports, SPORTS, type SportSlug } from '@fantasy-arena/shared/sports';
import { useParams } from 'next/navigation';
import { useMemo, useState } from 'react';

import { Nav } from '@/components/Nav';
import { api } from '@/lib/api';

export default function TeamBuilderPage() {
  const params = useParams<{ id: string }>();
  const matchId = params.id;
  const players = useQuery({
    queryKey: ['players', matchId],
    queryFn: () => api.matchPlayers(matchId),
    enabled: !!matchId,
  });

  // For demo, default to cricket; production would derive from match.sport.
  const [sport] = useState<SportSlug>('cricket');
  const cfg = SPORTS[sport];

  const [selected, setSelected] = useState<Set<string>>(new Set());

  const totalCredits = useMemo(() => {
    if (!players.data) return 0;
    return players.data.filter((p) => selected.has(p.id)).reduce((s, p) => s + p.credits, 0);
  }, [players.data, selected]);

  const remaining = (cfg.creditBudget - totalCredits).toFixed(1);

  function toggle(id: string, credits: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < cfg.teamSize && totalCredits + credits <= cfg.creditBudget + 0.01) {
        next.add(id);
      }
      return next;
    });
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Build your team</h1>
        <div className="mt-2 flex flex-wrap gap-3 text-sm">
          <span className="pill bg-slate-800 text-slate-200">
            {selected.size} / {cfg.teamSize} selected
          </span>
          <span className="pill bg-slate-800 text-slate-200">
            Credits left: {remaining}
          </span>
          <span className="pill bg-slate-800 text-slate-200">
            Sport: {listSports().find((s) => s.slug === sport)?.name}
          </span>
        </div>

        <div className="mt-6 grid gap-2 md:grid-cols-2">
          {(players.data ?? []).map((p) => (
            <button
              key={p.id}
              onClick={() => toggle(p.id, p.credits)}
              className={`flex items-center justify-between rounded-lg border px-4 py-2 text-left ${
                selected.has(p.id)
                  ? 'border-brand-500 bg-brand-900/40'
                  : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="font-medium">{p.full_name}</div>
                <div className="text-xs text-slate-400">{p.team_name} · {p.role}</div>
              </div>
              <div className="text-right text-sm font-mono">{p.credits.toFixed(1)}</div>
            </button>
          ))}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            disabled={selected.size !== cfg.teamSize}
            className="btn-primary disabled:opacity-50"
          >
            Choose captain & vice-captain →
          </button>
        </div>
      </main>
    </>
  );
}
