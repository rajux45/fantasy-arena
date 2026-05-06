import { Nav } from '@/components/Nav';

export default function HowItWorksPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">How it works</h1>
        <ol className="mt-6 space-y-4 text-slate-200">
          <Step n={1} title="Sign up & verify KYC" body="18+ only. Submit PAN + Aadhaar + DOB. Verification typically takes a few minutes." />
          <Step n={2} title="Add funds" body="UPI / netbanking / card via Razorpay. GST 28% is collected inclusive (transparent breakup shown)." />
          <Step n={3} title="Pick a contest" body="Mega (lakhs of slots), Head-to-head (1v1), Practice (free), Private (invite-only)." />
          <Step n={4} title="Build a team" body="Per-sport rules: cricket 11 + 100 credits, football 11, kabaddi 7, basketball 5. Pick captain (2x) + vice-captain (1.5x)." />
          <Step n={5} title="Score live" body="Points update in real time via WebSocket as the match plays out." />
          <Step n={6} title="Get paid" body="Winnings auto-credited after match ends. Withdraw to bank — 30% TDS deducted at source on net winnings." />
        </ol>
      </main>
    </>
  );
}

function Step({ n, title, body }: { n: number; title: string; body: string }) {
  return (
    <li className="flex gap-4">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-700 font-bold">{n}</span>
      <div>
        <div className="font-semibold">{title}</div>
        <p className="mt-1 text-sm text-slate-400">{body}</p>
      </div>
    </li>
  );
}
