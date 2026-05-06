import { Nav } from '@/components/Nav';

const EVENTS = [
  { ts: '10:00:01', actor: 'system', kind: 'match.start', detail: 'IPL: MI vs CSK kicked off' },
  { ts: '10:14:32', actor: 'admin@fa.in', kind: 'kyc.approve', detail: 'kyc-3 approved (user1@example.com)' },
  { ts: '10:16:11', actor: 'admin@fa.in', kind: 'withdrawal.approve', detail: 'wd-2 approved (₹6300 net)' },
  { ts: '10:25:00', actor: 'system', kind: 'ledger.reconcile', detail: 'OK — 0 imbalances' },
  { ts: '10:26:18', actor: 'system', kind: 'fraud.flag', detail: 'user u-1042 — 4 deposit retries from same IP' },
];

export default function AdminAuditPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Admin · Audit log</h1>
        <p className="mt-1 text-sm text-slate-400">Append-only log. Every privileged action and every system event is recorded.</p>
        <table className="card mt-4 w-full text-sm">
          <thead className="text-left text-slate-400"><tr><th className="pb-2">Time</th><th>Actor</th><th>Kind</th><th>Detail</th></tr></thead>
          <tbody>
            {EVENTS.map((e, i) => (
              <tr key={i} className="border-t border-slate-800">
                <td className="py-2 font-mono">{e.ts}</td>
                <td>{e.actor}</td>
                <td><span className="pill bg-slate-700 text-slate-200">{e.kind}</span></td>
                <td className="text-slate-300">{e.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </>
  );
}
