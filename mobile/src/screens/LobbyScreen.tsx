import { listSports, type SportSlug } from '@fantasy-arena/shared/sports';
import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { apiGet } from '../api';

interface Match {
  id: string;
  short_name: string;
  home_team: string;
  away_team: string;
  starts_at: string;
}

export function LobbyScreen() {
  const [sport, setSport] = useState<SportSlug>('cricket');
  const [matches, setMatches] = useState<Match[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    setMatches(null);
    setErr(null);
    apiGet<Match[]>(`/v1/matches?sport=${sport}`).then(setMatches).catch((e) => setErr(String(e)));
  }, [sport]);

  return (
    <ScrollView contentContainerStyle={styles.root}>
      <View style={styles.tabs}>
        {listSports().map((s) => (
          <Pressable
            key={s.slug}
            onPress={() => setSport(s.slug)}
            style={[styles.tab, sport === s.slug && styles.tabActive]}
          >
            <Text style={[styles.tabText, sport === s.slug && styles.tabTextActive]}>
              {s.emoji} {s.name}
            </Text>
          </Pressable>
        ))}
      </View>
      {err ? <Text style={styles.err}>{err}</Text> : null}
      {(matches ?? []).map((m) => (
        <View key={m.id} style={styles.card}>
          <Text style={styles.cardTitle}>{m.home_team} vs {m.away_team}</Text>
          <Text style={styles.cardMeta}>Starts {new Date(m.starts_at).toLocaleString('en-IN')}</Text>
        </View>
      ))}
      {matches && matches.length === 0 ? (
        <Text style={styles.empty}>No matches yet for this sport.</Text>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { padding: 16, gap: 12 },
  tabs: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  tab: { paddingVertical: 6, paddingHorizontal: 12, borderRadius: 20, backgroundColor: '#1e293b' },
  tabActive: { backgroundColor: '#7c3aed' },
  tabText: { color: '#cbd5e1' },
  tabTextActive: { color: '#fff' },
  card: { backgroundColor: '#1e293b', padding: 14, borderRadius: 12 },
  cardTitle: { color: '#f8fafc', fontWeight: '600', fontSize: 16 },
  cardMeta: { color: '#94a3b8', marginTop: 4 },
  err: { color: '#f87171' },
  empty: { color: '#94a3b8' },
});
