import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { RootStackParamList } from '../App';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export function HomeScreen({ navigation }: Props) {
  return (
    <View style={styles.root}>
      <Text style={styles.title}>Fantasy Arena</Text>
      <Text style={styles.subtitle}>Skill-based fantasy + provably-fair social casino.</Text>
      <View style={styles.buttons}>
        <Btn label="Browse contests" onPress={() => navigation.navigate('Lobby')} />
        <Btn label="Casino" onPress={() => navigation.navigate('Casino')} />
        <Btn label="Wallet" onPress={() => navigation.navigate('Wallet')} />
        <Btn label="Log in" onPress={() => navigation.navigate('Login')} primary />
      </View>
      <Text style={styles.legal}>
        Real-money fantasy not available in AS, OD, NL, SK, TG, AP. Casino is play-money only — no cash-out.
      </Text>
    </View>
  );
}

function Btn({ label, onPress, primary }: { label: string; onPress: () => void; primary?: boolean }) {
  return (
    <Pressable
      onPress={onPress}
      style={[styles.btn, primary && styles.btnPrimary]}
    >
      <Text style={[styles.btnText, primary && styles.btnTextPrimary]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, padding: 24, justifyContent: 'center' },
  title: { fontSize: 32, fontWeight: '700', color: '#f8fafc' },
  subtitle: { marginTop: 12, color: '#cbd5e1', fontSize: 16 },
  buttons: { marginTop: 32, gap: 12 },
  btn: {
    paddingVertical: 14,
    paddingHorizontal: 18,
    backgroundColor: '#1e293b',
    borderRadius: 12,
  },
  btnPrimary: { backgroundColor: '#7c3aed' },
  btnText: { color: '#e2e8f0', fontSize: 16, fontWeight: '500', textAlign: 'center' },
  btnTextPrimary: { color: '#ffffff' },
  legal: { marginTop: 32, color: '#64748b', fontSize: 12 },
});
