'use client';

import { useQuery } from '@tanstack/react-query';
import { formatCoins, formatINR } from '@fantasy-arena/shared/money';

import { Nav } from '@/components/Nav';
import { api } from '@/lib/api';

export default function WalletPage() {
  const wallet = useQuery({ queryKey: ['wallet'], queryFn: () => api.myWallet() });

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Wallet</h1>
        {wallet.isLoading ? (
          <p className="mt-4 text-slate-400">Loading…</p>
        ) : wallet.error ? (
          <p className="mt-4 text-red-400">Sign in first to see your wallet.</p>
        ) : wallet.data ? (
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <Stat label="Deposit" value={formatINR(wallet.data.deposit_paise)} sub="Available + KYC required to withdraw" />
            <Stat label="Winnings" value={formatINR(wallet.data.winnings_paise)} sub="Withdrawable; TDS at withdrawal" />
            <Stat label="Bonus" value={formatINR(wallet.data.bonus_paise)} sub="Play-only" />
            <Stat label="Casino coins" value={formatCoins(wallet.data.casino_coins)} sub="No cash-out — virtual only" warn />
          </div>
        ) : null}
      </main>
    </>
  );
}

function Stat({ label, value, sub, warn }: { label: string; value: string; sub?: string; warn?: boolean }) {
  return (
    <div className="card">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-1 text-3xl font-semibold">{value}</div>
      {sub ? <div className={`mt-2 text-xs ${warn ? 'text-amber-300' : 'text-slate-500'}`}>{sub}</div> : null}
    </div>
  );
}
