import { formatCurrency } from '../../utils/currency';
import { Skeleton } from '../Skeleton/Skeleton';
import './BalanceCard.css';

interface BalanceCardProps {
  /** Label above the amount, e.g. "Available balance". */
  label?: string;
  balance: number;
  currency: string;
}

/**
 * Displays an already-computed balance. This component receives balance
 * data as a prop and ONLY formats/renders it — it never calculates,
 * modifies, or hardcodes an account balance, and it never touches
 * transaction data. When the mock dashboard service is swapped for a
 * real API, this component does not change.
 */
export function BalanceCard({ label = 'Available balance', balance, currency }: BalanceCardProps) {
  return (
    <section className="balance-card" aria-label={label}>
      <p className="balance-card__label">{label}</p>
      <p className="balance-card__amount">{formatCurrency(balance, currency)}</p>
    </section>
  );
}

/** Skeleton counterpart shown while dashboard data is loading. */
export function BalanceCardSkeleton() {
  return (
    <section className="balance-card" aria-hidden="true">
      <Skeleton width="140px" height="16px" />
      <Skeleton width="220px" height="40px" className="balance-card__amount-skeleton" />
    </section>
  );
}
