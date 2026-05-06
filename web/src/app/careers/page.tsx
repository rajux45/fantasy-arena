import { Nav } from '@/components/Nav';

export default function CareersPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Careers</h1>
        <p className="mt-1 text-sm text-slate-400">Build the next-generation fantasy + social casino in India.</p>
        <div className="mt-6 space-y-3">
          {[
            { role: 'Senior Backend Engineer', loc: 'Bengaluru / Remote', stack: 'Python, FastAPI, Postgres' },
            { role: 'Senior Frontend Engineer', loc: 'Bengaluru / Remote', stack: 'Next.js, TypeScript, React Native' },
            { role: 'SRE / Platform Engineer', loc: 'Bengaluru / Remote', stack: 'Kubernetes, Terraform, observability' },
            { role: 'KYC & Compliance Lead', loc: 'Bengaluru', stack: 'AML, FIU-IND, AIGF/FIFS' },
            { role: 'Anti-fraud Analyst', loc: 'Bengaluru / Remote', stack: 'SQL, Python, ML' },
          ].map((j) => (
            <div key={j.role} className="card">
              <div className="font-semibold">{j.role}</div>
              <div className="text-sm text-slate-400">{j.loc} · {j.stack}</div>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-slate-400">Apply: <a className="text-brand-400 hover:underline" href="mailto:careers@fantasy-arena.in">careers@fantasy-arena.in</a></p>
      </main>
    </>
  );
}
