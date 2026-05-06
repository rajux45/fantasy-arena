/** Money utilities: paise <-> rupees, INR formatting. Always integer paise on the wire. */

export const PAISE_PER_RUPEE = 100;

export function paiseToRupees(paise: number): number {
  return Math.round(paise) / PAISE_PER_RUPEE;
}

export function rupeesToPaise(rupees: number): number {
  return Math.round(rupees * PAISE_PER_RUPEE);
}

export function formatINR(paise: number, opts: { showDecimals?: boolean } = {}): string {
  const rupees = paiseToRupees(paise);
  const formatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: opts.showDecimals ? 2 : 0,
    minimumFractionDigits: opts.showDecimals ? 2 : 0,
  });
  return formatter.format(rupees);
}

export function formatCoins(coins: number): string {
  if (coins >= 1_00_00_000) return `${(coins / 1_00_00_000).toFixed(1)}Cr`;
  if (coins >= 1_00_000) return `${(coins / 1_00_000).toFixed(1)}L`;
  if (coins >= 1_000) return `${(coins / 1_000).toFixed(1)}K`;
  return String(coins);
}
