'use client';

import { useQuery } from '@tanstack/react-query';

import { Nav } from '@/components/Nav';
import { api, clearTokens } from '@/lib/api';

export default function ProfilePage() {
  const me = useQuery({ queryKey: ['me'], queryFn: () => api.me() });

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Profile</h1>
        {me.isLoading ? (
          <p className="mt-4 text-slate-400">Loading…</p>
        ) : me.error ? (
          <p className="mt-4 text-red-400">Please sign in.</p>
        ) : me.data ? (
          <div className="card mt-6 space-y-2 text-sm">
            <Row label="Name" value={me.data.full_name ?? '—'} />
            <Row label="Email" value={me.data.email ?? '—'} />
            <Row label="Phone" value={me.data.phone ?? '—'} />
            <Row label="Role" value={me.data.role} />
            <Row label="KYC" value={me.data.kyc_status} />
            <Row label="State" value={me.data.state_code ?? 'not set'} />
            <Row label="Referral code" value={me.data.referral_code} />
            <Row label="Age verified" value={me.data.is_age_verified ? 'yes' : 'no'} />
            <button
              onClick={() => {
                clearTokens();
                window.location.href = '/';
              }}
              className="btn-secondary mt-2"
            >
              Log out
            </button>
          </div>
        ) : null}
      </main>
    </>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-800 py-1.5 last:border-b-0">
      <span className="text-slate-400">{label}</span>
      <span className="font-mono">{value}</span>
    </div>
  );
}
