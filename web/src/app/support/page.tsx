'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

const FAQS = [
  { q: 'Is real-money fantasy legal in my state?', a: 'Legal in most Indian states; restricted in AS, OD, NL, SK, TG, AP. We auto-detect from your KYC state code.' },
  { q: 'Can I withdraw casino coins as cash?', a: 'No. Casino coins are virtual play-money only. There is no cash-out path. This is by design and by law.' },
  { q: 'How is TDS calculated on withdrawals?', a: 'TDS at 30% on net winnings under Sec 194BA. Calculated at the moment you request a withdrawal.' },
  { q: 'How do I verify a casino round was fair?', a: 'After rotating your seed, paste the revealed server seed into our verifier; SHA-256(seed) must match the original hash you saw before play.' },
  { q: 'How long do withdrawals take?', a: 'Typically 24 hours for verified KYC users. First withdrawal may take up to 48 hours for fraud checks.' },
  { q: 'What if I want to take a break?', a: 'Use Responsible Gaming → Self-exclude. Choose 1d / 7d / 30d / 6mo / permanent. While excluded, you cannot deposit or play.' },
];

export default function SupportPage() {
  const [open, setOpen] = useState(0);
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Help & support</h1>
        <p className="mt-1 text-sm text-slate-400">
          Email <a className="text-brand-400 hover:underline" href="mailto:support@fantasy-arena.in">support@fantasy-arena.in</a>
          {' · '}
          Live chat 9am–11pm IST.
        </p>

        <h2 className="mt-6 text-lg font-semibold">FAQs</h2>
        <div className="mt-3 space-y-2">
          {FAQS.map((f, i) => (
            <div key={i} className="card">
              <button onClick={() => setOpen(open === i ? -1 : i)} className="flex w-full items-center justify-between text-left">
                <span className="font-medium">{f.q}</span>
                <span className="text-slate-500">{open === i ? '−' : '+'}</span>
              </button>
              {open === i ? <p className="mt-2 text-sm text-slate-300">{f.a}</p> : null}
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
