/** Sport definitions, team rules, and player roles. */

export type SportSlug = 'cricket' | 'football' | 'kabaddi' | 'basketball';

export type PlayerRole =
  | 'wicket_keeper'
  | 'batsman'
  | 'all_rounder'
  | 'bowler'
  | 'goalkeeper'
  | 'defender'
  | 'midfielder'
  | 'forward'
  | 'raider'
  | 'defender_kabaddi'
  | 'all_rounder_kabaddi'
  | 'point_guard'
  | 'shooting_guard'
  | 'small_forward'
  | 'power_forward'
  | 'center';

export interface SportConfig {
  slug: SportSlug;
  name: string;
  emoji: string;
  teamSize: number;
  creditBudget: number;
  roleRules: Record<PlayerRole, [min: number, max: number]> | null;
  maxFromOneSide: number;
}

export const SPORTS: Record<SportSlug, SportConfig> = {
  cricket: {
    slug: 'cricket',
    name: 'Cricket',
    emoji: '🏏',
    teamSize: 11,
    creditBudget: 100,
    maxFromOneSide: 7,
    roleRules: {
      wicket_keeper: [1, 4],
      batsman: [3, 6],
      all_rounder: [1, 4],
      bowler: [3, 6],
    } as Partial<Record<PlayerRole, [number, number]>> as Record<PlayerRole, [number, number]>,
  },
  football: {
    slug: 'football',
    name: 'Football',
    emoji: '⚽',
    teamSize: 11,
    creditBudget: 100,
    maxFromOneSide: 7,
    roleRules: {
      goalkeeper: [1, 1],
      defender: [3, 5],
      midfielder: [3, 5],
      forward: [1, 3],
    } as Partial<Record<PlayerRole, [number, number]>> as Record<PlayerRole, [number, number]>,
  },
  kabaddi: {
    slug: 'kabaddi',
    name: 'Kabaddi',
    emoji: '🤼',
    teamSize: 7,
    creditBudget: 100,
    maxFromOneSide: 5,
    roleRules: {
      raider: [2, 4],
      defender_kabaddi: [2, 4],
      all_rounder_kabaddi: [1, 3],
    } as Partial<Record<PlayerRole, [number, number]>> as Record<PlayerRole, [number, number]>,
  },
  basketball: {
    slug: 'basketball',
    name: 'Basketball',
    emoji: '🏀',
    teamSize: 5,
    creditBudget: 100,
    maxFromOneSide: 4,
    roleRules: null,
  },
};

export function listSports(): SportConfig[] {
  return Object.values(SPORTS);
}
