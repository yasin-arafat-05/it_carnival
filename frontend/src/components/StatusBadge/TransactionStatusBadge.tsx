import type { TransactionStatus } from '../../types/dashboard';
import './StatusBadge.css';

interface TransactionStatusBadgeProps {
  status: TransactionStatus;
}

const STATUS_LABEL: Record<TransactionStatus, string> = {
  completed: 'Completed',
  pending: 'Pending',
  failed: 'Failed',
  cancelled: 'Cancelled',
  reversed: 'Reversed',
  reversal_in_progress: 'Reversal in progress',
};

/**
 * Feature 14 — Transaction Status UI.
 *
 * Small text+color status pill for a transaction's state (amber/pending,
 * green/completed, red/failed, gray/cancelled). Shares markup and styling
 * conventions with the account `StatusBadge` (same CSS file, additional
 * modifier classes) — never color-only, always a readable label. Reused
 * anywhere a transaction's status needs to be shown: the transaction
 * list on the Dashboard, the Send Money result screen, and (later)
 * transaction history/detail views — it only ever receives a
 * `TransactionStatus` value as a prop, never derives one itself.
 */
export function TransactionStatusBadge({ status }: TransactionStatusBadgeProps) {
  return <span className={`status-badge status-badge--${status}`}>{STATUS_LABEL[status]}</span>;
}
