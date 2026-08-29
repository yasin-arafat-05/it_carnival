/**
 * Shared currency formatting helper. Pure display formatting only — no
 * calculation, no rounding decisions beyond fixed 2 decimal places.
 */
export function formatCurrency(amount: number, currency: string): string {
  const formatted = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Math.abs(amount));
  return `${currency} ${formatted}`;
}
