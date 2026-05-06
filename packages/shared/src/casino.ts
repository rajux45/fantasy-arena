/** Casino game definitions and provably-fair verification helper. */

export type CasinoGameSlug =
  | 'crash'
  | 'plinko'
  | 'mines'
  | 'dice'
  | 'roulette'
  | 'slots'
  | 'blackjack';

export interface CasinoGame {
  slug: CasinoGameSlug;
  name: string;
  description: string;
  minBet: number;
  maxBet: number;
}

export const CASINO_GAMES: Record<CasinoGameSlug, CasinoGame> = {
  crash: { slug: 'crash', name: 'Crash', description: 'Cash out before the multiplier crashes.', minBet: 10, maxBet: 10_00_000 },
  plinko: { slug: 'plinko', name: 'Plinko', description: 'Drop the ball, choose risk.', minBet: 10, maxBet: 10_00_000 },
  mines: { slug: 'mines', name: 'Mines', description: 'Pick safe tiles, avoid bombs.', minBet: 10, maxBet: 10_00_000 },
  dice: { slug: 'dice', name: 'Dice', description: 'Predict over/under a target.', minBet: 10, maxBet: 10_00_000 },
  roulette: { slug: 'roulette', name: 'Roulette', description: 'European single-zero wheel.', minBet: 10, maxBet: 10_00_000 },
  slots: { slug: 'slots', name: 'Slots', description: 'Classic 5-reel paylines.', minBet: 10, maxBet: 10_00_000 },
  blackjack: { slug: 'blackjack', name: 'Blackjack', description: 'Beat the dealer to 21.', minBet: 10, maxBet: 10_00_000 },
};

/** Compute SHA-256 of a server seed in hex. Used by the player to verify the server's pre-commitment. */
export async function sha256Hex(input: string): Promise<string> {
  const g = globalThis as unknown as {
    TextEncoder?: { new (): { encode(s: string): Uint8Array } };
    crypto?: { subtle?: { digest(alg: string, data: Uint8Array): Promise<ArrayBuffer> } };
  };
  if (!g.TextEncoder || !g.crypto?.subtle) {
    throw new Error('Web Crypto API not available in this runtime; verify on web.');
  }
  const data = new g.TextEncoder().encode(input);
  const buf = await g.crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function verifyServerSeed(serverSeed: string, expectedHash: string): Promise<boolean> {
  const computed = await sha256Hex(serverSeed);
  return computed === expectedHash;
}
