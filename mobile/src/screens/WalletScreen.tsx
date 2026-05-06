import { formatCoins, formatINR } from '@fantasy-arena/shared/money';
import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { apiGet } from '../api';

interface WalletDto {
  deposit_paise: number;
  winnings_paise: number;
  bonus_paise: number;
  casino_coins: number;
}

export function WalletScreen() {
  const [w, setW] = useState<WalletDto | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    apiGet<WalletDto>('/v1/wallet/me').then(setW).catch((e) => setErr(String(e)));
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.root}>
      {err ? <Text style={styles.err}>{err}</Text> : null}
      {w ? (
        <>
          <Card label="Deposit" value={formatINR(w.deposit_paise)} />
          <Card label="Winnings" value={formatINR(w.winnings_paise)} />
          <Card label="Bonus" value={formatINR(w.bonus_paise)} />
          <Card label="Casino coins" value={formatCoins(w.casino_coins)} sub="Virtual only — no cash-out" />
        </>
      ) : !err ? <Text style={styles.muted}>Loading…</Text> : null}
    </ScrollView>
  );
}

function Card({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <View style={styles.card}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
      {sub ? <Text style={styles.sub}>{sub}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { padding: 16, gap: 12 },
  card: { backgroundColor: '#1e293b', padding: 16, borderRadius: 12 },
  label: { color: '#94a3b8' },
  value: { color: '#f8fafc', fontSize: 26, fontWeight: '700', marginTop: 4 },
  sub: { color: '#fbbf24', marginTop: 4, fontSize: 12 },
  err: { color: '#f87171' },
  muted: { color: '#94a3b8' },
});
