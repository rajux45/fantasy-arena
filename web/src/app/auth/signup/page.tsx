'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Nav } from '@/components/Nav';
import { api, setTokens } from '@/lib/api';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [agreed, setAgreed] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!agreed) {
      setError('You must confirm you are 18+ and accept the legal terms.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const tokens = await api.signupEmail({ email, password, full_name: fullName || undefined });
      setTokens(tokens);
      router.push('/lobby');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-md px-4 py-12">
        <h1 className="text-3xl font-semibold">Create your account</h1>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm text-slate-300">Full name</span>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">Email</span>
            <input
              required
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">Password (min 8 chars)</span>
            <input
              required
              minLength={8}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
          </label>
          <label className="flex items-start gap-2 text-sm text-slate-300">
            <input
              required
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-1"
            />
            <span>
              I confirm I am 18+ and accept the{' '}
              <a href="/legal" className="text-brand-400 hover:underline">Legal & Responsible Gaming</a> terms.
            </span>
          </label>
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
            {loading ? 'Creating…' : 'Sign up'}
          </button>
        </form>
      </main>
    </>
  );
}
