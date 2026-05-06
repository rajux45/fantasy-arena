'use client';

import { sha256Hex } from '@fantasy-arena/shared/casino';
import { useState } from 'react';

import { Nav } from '@/components/Nav';

export default function ProvablyFairPage() {
  const [seed, setSeed] = useState('');
  const [expectedHash, setExpectedHash] = useState('');
  const [result, setResult] = useState<{ computed: string; ok: boolean } | null>(null);

  async function verify() {
    const computed = await sha256Hex(seed);
    setResult({ computed, ok: computed.toLowerCase() === expectedHash.toLowerCase() });
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Provably fair — explained</h1>

        <section className="card mt-6 space-y-3 text-sm text-slate-300">
          <h2 className="text-lg font-semibold text-white">How it works</h2>
          <ol className="ml-4 list-decimal space-y-2">
            <li>Before you play, the server commits to a secret <strong>server_seed</strong> by publishing only its SHA-256 hash.</li>
            <li>You play one or many rounds; each round uses the formula:
              <pre className="mt-1 rounded bg-slate-900 p-2 text-xs">HMAC-SHA256(server_seed, client_seed:nonce:cursor)</pre>
            </li>
            <li>When you rotate seeds, the server reveals the original <strong>server_seed</strong>.</li>
            <li>You compute SHA-256(revealed_seed) and check it matches the original hash. If yes, the server could not have manipulated outcomes.</li>
          </ol>
        </section>

        <section className="card mt-6 space-y-3">
          <h2 className="text-lg font-semibold">Verifier</h2>
          <label className="block text-sm">
            <span className="text-slate-300">Revealed server seed</span>
            <input
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-300">Original (pre-committed) hash</span>
            <input
              value={expectedHash}
              onChange={(e) => setExpectedHash(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs"
            />
          </label>
          <button onClick={verify} disabled={!seed || !expectedHash} className="btn-primary disabled:opacity-50">
            Verify
          </button>
          {result ? (
            <div className={`rounded-lg p-3 text-sm ${result.ok ? 'bg-emerald-900/30 text-emerald-200' : 'bg-red-900/30 text-red-200'}`}>
              <div>Computed SHA-256: <span className="font-mono text-xs">{result.computed}</span></div>
              <div className="mt-1 font-semibold">{result.ok ? 'Match — server seed is verified.' : 'Mismatch — DO NOT TRUST.'}</div>
            </div>
          ) : null}
        </section>
      </main>
    </>
  );
}
