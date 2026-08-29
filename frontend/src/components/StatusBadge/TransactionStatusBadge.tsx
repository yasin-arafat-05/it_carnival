import type { TransactionStatus } from '../../types/dashboard';
import './StatusBadge.css';

interface TransactionStatusBadgeProps {
  status: TransactionStatus;
}

const STATUS_LABEL: Record<TransactionStatus, string> = {
  completed: 'Completed',
  pending: 'Pending',
  failed: 'Failed',
};

/**
 * Small text+color status pill for a transaction's state. Shares markup
 * and styling conventions with the account `StatusBadge` (same CSS file,
 * additional modifier classes) — never color-only, always a readable label.
 */
export function TransactionStatusBadge({ status }: TransactionStatusBadgeProps) {
  return <span className={`status-badge status-badge--${status}`}>{STATUS_LABEL[status]}</span>;
}
