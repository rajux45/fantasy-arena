import { CASINO_GAMES } from '@fantasy-arena/shared/casino';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

export function CasinoScreen() {
  return (
    <ScrollView contentContainerStyle={styles.root}>
      <Text style={styles.heading}>Social casino (play-money)</Text>
      <Text style={styles.warn}>Coins are virtual — no real-money cash-out. Ever.</Text>
      <View style={styles.grid}>
        {Object.values(CASINO_GAMES).map((g) => (
          <View key={g.slug} style={styles.card}>
            <Text style={styles.cardTitle}>{g.name}</Text>
            <Text style={styles.cardDesc}>{g.description}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { padding: 16, gap: 12 },
  heading: { fontSize: 22, fontWeight: '700', color: '#f8fafc' },
  warn: { color: '#fbbf24', fontSize: 12 },
  grid: { gap: 12, marginTop: 8 },
  card: { backgroundColor: '#1e293b', padding: 14, borderRadius: 12 },
  cardTitle: { fontSize: 16, fontWeight: '600', color: '#f8fafc' },
  cardDesc: { color: '#94a3b8', marginTop: 4 },
});
