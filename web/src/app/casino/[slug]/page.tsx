'use client';

import { CASINO_GAMES, type CasinoGameSlug, verifyServerSeed } from '@fantasy-arena/shared/casino';
import { useParams } from 'next/navigation';
import { useState } from 'react';

import { Nav } from '@/components/Nav';
import { api } from '@/lib/api';

export default function CasinoGamePage() {
  const { slug } = useParams<{ slug: CasinoGameSlug }>();
  const game = CASINO_GAMES[slug];
  const [bet, setBet] = useState(100);
  const [target, setTarget] = useState(50.5);
  const [direction, setDirection] = useState<'over' | 'under'>('over');
  const [result, setResult] = useState<{ multiplier: number; payout: number; outcome: unknown; serverSeedHash: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);

  async function handlePlay() {
    setError(null);
    try {
      const out = await api.playCasino({
        game: slug,
        bet_coins: bet,
        bet_input:
          slug === 'dice'
            ? { target, direction }
            : slug === 'crash'
              ? { auto_cashout: 1.5 }
              : slug === 'plinko'
                ? { rows: 12, risk: 'medium' }
                : slug === 'mines'
                  ? { bombs: 3, picks: 3 }
                  : slug === 'roulette'
                    ? { bet_type: 'red' }
                    : {},
      });
      setResult({ multiplier: out.multiplier, payout: out.payout_coins, outcome: out.outcome, serverSeedHash: out.server_seed_hash });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Play failed');
    }
  }

  async function handleVerifyRotated() {
    setVerifying(true);
    try {
      const r = await api.rotateCasinoSeed();
      if (r.revealed_server_seed && result) {
        const ok = await verifyServerSeed(r.revealed_server_seed, result.serverSeedHash);
        alert(ok ? 'Verified: server seed matches the pre-committed hash.' : 'Verification failed!');
      }
    } finally {
      setVerifying(false);
    }
  }

  if (!game) return <p className="p-8">Unknown game</p>;

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold capitalize">{game.name}</h1>
        <p className="text-sm text-slate-400">{game.description}</p>

        <div className="card mt-6 space-y-4">
          <label className="block">
            <span className="text-sm text-slate-300">Bet (coins)</span>
            <input
              type="number"
              min={1}
              value={bet}
              onChange={(e) => setBet(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>

          {slug === 'dice' ? (
            <div className="grid grid-cols-2 gap-3">
              <label className="block">
                <span className="text-sm text-slate-300">Target (0–100)</span>
                <input
                  type="number"
                  step={0.01}
                  value={target}
                  onChange={(e) => setTarget(Number(e.target.value))}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-slate-300">Direction</span>
                <select
                  value={direction}
                  onChange={(e) => setDirection(e.target.value as 'over' | 'under')}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
                >
                  <option value="over">Over</option>
                  <option value="under">Under</option>
                </select>
              </label>
            </div>
          ) : null}

          <button onClick={handlePlay} className="btn-primary w-full">Play one round</button>

          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          {result ? (
            <div className="rounded-lg bg-slate-800/40 p-4 text-sm">
              <div>Multiplier: <span className="font-mono">{result.multiplier}x</span></div>
              <div>Payout: <span className="font-mono">{result.payout} coins</span></div>
              <details className="mt-2">
                <summary className="cursor-pointer text-slate-400">Outcome detail</summary>
                <pre className="mt-2 overflow-auto text-xs">{JSON.stringify(result.outcome, null, 2)}</pre>
              </details>
              <button onClick={handleVerifyRotated} className="btn-secondary mt-3 text-xs" disabled={verifying}>
                Rotate & verify server seed
              </button>
            </div>
          ) : null}
        </div>
      </main>
    </>
  );
}
