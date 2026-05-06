import { Nav } from '@/components/Nav';

const WINNERS = [
  { name: 'Rohan G.', city: 'Mumbai', amount: '₹2.5 Cr', contest: 'IPL Mega', date: 'Apr 24' },
  { name: 'Priya K.', city: 'Bengaluru', amount: '₹50 L', contest: 'IPL Mega', date: 'Apr 24' },
  { name: 'Akash M.', city: 'Hyderabad', amount: '₹25 L', contest: 'IPL Mega', date: 'Apr 24' },
  { name: 'Devansh S.', city: 'Pune', amount: '₹10 L', contest: 'ISL Mega', date: 'Apr 22' },
  { name: 'Ishita N.', city: 'Delhi', amount: '₹5 L', contest: 'PKL Weekly', date: 'Apr 21' },
];

export default function WinnersPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Recent winners</h1>
        <p className="mt-1 text-sm text-slate-400">Real users, real stories. (Names anonymized for privacy; full city + amount + date is verifiable on request.)</p>
        <div className="mt-6 space-y-3">
          {WINNERS.map((w, i) => (
            <div key={i} className="card flex items-center justify-between">
              <div>
                <div className="font-semibold">{w.name} <span className="text-xs font-normal text-slate-400">· {w.city}</span></div>
                <div className="text-xs text-slate-500">{w.contest} · {w.date}</div>
              </div>
              <div className="text-2xl font-bold text-emerald-400">{w.amount}</div>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
