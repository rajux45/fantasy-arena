'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

export default function KycPage() {
  const [pan, setPan] = useState('');
  const [aadhaar, setAadhaar] = useState('');
  const [dob, setDob] = useState('');
  const [state, setState] = useState('MH');
  const [status, setStatus] = useState<'idle' | 'submitted' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  const restricted = ['AS', 'OD', 'NL', 'SK', 'TG', 'AP'];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(pan)) {
      setError('PAN format invalid (e.g., ABCDE1234F).');
      return;
    }
    if (!/^\d{12}$/.test(aadhaar.replace(/\s+/g, ''))) {
      setError('Aadhaar must be 12 digits.');
      return;
    }
    setStatus('submitted');
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-md px-4 py-8">
        <h1 className="text-2xl font-semibold">KYC verification</h1>
        <p className="mt-2 text-sm text-slate-400">
          Required for real-money deposits and withdrawals (Sec 194BA TDS compliance).
        </p>

        {restricted.includes(state) ? (
          <div className="mt-4 rounded-lg border border-amber-700 bg-amber-900/30 p-3 text-sm text-amber-200">
            Real-money fantasy is restricted in {state}. You can still play the social casino in coins.
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="mt-6 space-y-3">
          <Field label="PAN (e.g., ABCDE1234F)" value={pan} onChange={setPan} placeholder="ABCDE1234F" />
          <Field label="Aadhaar (12 digits)" value={aadhaar} onChange={setAadhaar} placeholder="1234 5678 9012" />
          <Field label="Date of birth" value={dob} onChange={setDob} type="date" />
          <label className="block">
            <span className="text-sm text-slate-300">State</span>
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            >
              {['MH', 'KA', 'DL', 'TN', 'WB', 'GJ', 'UP', 'AS', 'OD', 'NL', 'SK', 'TG', 'AP'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          {status === 'submitted' ? (
            <p className="text-sm text-emerald-400">
              Submitted! Verification typically takes a few minutes. You&apos;ll get a notification when approved.
            </p>
          ) : (
            <button type="submit" className="btn-primary w-full">Submit for verification</button>
          )}
        </form>
      </main>
    </>
  );
}

function Field({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm text-slate-300">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
      />
    </label>
  );
}
