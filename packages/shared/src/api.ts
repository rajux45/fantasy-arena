/** Common API types reflected from the Pydantic schemas. */

import { z } from 'zod';

import type { CasinoGameSlug } from './casino';
import type { PlayerRole, SportSlug } from './sports';

export const TokenPair = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().default('bearer'),
});
export type TokenPair = z.infer<typeof TokenPair>;

export const Me = z.object({
  id: z.string(),
  email: z.string().nullable().optional(),
  phone: z.string().nullable().optional(),
  full_name: z.string().nullable().optional(),
  username: z.string().nullable().optional(),
  role: z.string(),
  kyc_status: z.string(),
  state_code: z.string().nullable().optional(),
  referral_code: z.string(),
  is_age_verified: z.boolean(),
  is_email_verified: z.boolean(),
  is_phone_verified: z.boolean(),
});
export type Me = z.infer<typeof Me>;

export const Wallet = z.object({
  deposit_paise: z.number().int(),
  winnings_paise: z.number().int(),
  bonus_paise: z.number().int(),
  casino_coins: z.number().int(),
  withdrawable_paise: z.number().int(),
});
export type Wallet = z.infer<typeof Wallet>;

export interface Match {
  id: string;
  sport: SportSlug;
  short_name: string;
  home_team: string;
  away_team: string;
  venue: string | null;
  starts_at: string;
  lineup_locks_at: string;
  status: 'upcoming' | 'live' | 'completed' | 'abandoned';
}

export interface Player {
  id: string;
  full_name: string;
  short_name: string | null;
  team_name: string;
  role: PlayerRole;
  credits: number;
}

export interface Contest {
  id: string;
  name: string;
  kind: 'mega' | 'head_to_head' | 'small' | 'practice' | 'private' | 'winner_takes_all';
  status: string;
  entry_fee_paise: number;
  prize_pool_paise: number;
  total_slots: number;
  filled_slots: number;
  max_teams_per_user: number;
  is_private: boolean;
  invite_code: string | null;
  guaranteed: boolean;
  rake_pct: number;
}

export interface BetIn {
  game: CasinoGameSlug;
  bet_coins: number;
  bet_input: Record<string, unknown>;
}

export interface RoundOut {
  id: string;
  game: CasinoGameSlug;
  bet_coins: number;
  payout_coins: number;
  multiplier: number;
  server_seed_hash: string;
  server_seed: string | null;
  client_seed: string;
  nonce: number;
  outcome: Record<string, unknown>;
  bet_input: Record<string, unknown>;
}
