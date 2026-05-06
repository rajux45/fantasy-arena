/** Browser-side API client. Reads access token from localStorage. */

import type { Contest, Match, Me, Player, RoundOut, TokenPair, Wallet } from '@fantasy-arena/shared/api';

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const ACCESS_KEY = 'fa.access';
const REFRESH_KEY = 'fa.refresh';

export function setTokens(t: TokenPair) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(ACCESS_KEY, t.access_token);
  window.localStorage.setItem(REFRESH_KEY, t.refresh_token);
}

export function clearTokens() {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  signupEmail: (body: { email: string; password: string; full_name?: string }) =>
    request<TokenPair>('/v1/auth/signup/email', { method: 'POST', body: JSON.stringify(body) }),
  loginEmail: (body: { email: string; password: string }) =>
    request<TokenPair>('/v1/auth/login/email', { method: 'POST', body: JSON.stringify(body) }),
  me: () => request<Me>('/v1/auth/me'),
  myWallet: () => request<Wallet>('/v1/wallet/me'),
  listSports: () => request<{ id: string; slug: string; name: string }[]>('/v1/sports'),
  listMatches: (sport?: string) =>
    request<Match[]>(`/v1/matches${sport ? `?sport=${sport}` : ''}`),
  matchPlayers: (id: string) => request<Player[]>(`/v1/matches/${id}/players`),
  matchContests: (id: string) => request<Contest[]>(`/v1/matches/${id}/contests`),
  myCasinoSeed: () =>
    request<{ server_seed_hash: string; client_seed: string; nonce: number }>('/v1/casino/seed'),
  rotateCasinoSeed: () =>
    request<{ revealed_server_seed: string | null; new_server_seed_hash: string; new_client_seed: string }>(
      '/v1/casino/seed/rotate',
      { method: 'POST' },
    ),
  playCasino: (body: { game: string; bet_coins: number; bet_input: Record<string, unknown> }) =>
    request<RoundOut>('/v1/casino/play', { method: 'POST', body: JSON.stringify(body) }),
  casinoPackages: () =>
    request<{ slug: string; price_paise: number; coins: number }[]>('/v1/casino/packages'),
};
