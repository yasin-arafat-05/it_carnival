import type { AccountStatus } from '../../types/auth';
import './StatusBadge.css';

interface StatusBadgeProps {
  status: AccountStatus;
}

const STATUS_LABEL: Record<AccountStatus, string> = {
  active: 'Active',
  suspended: 'Suspended',
};

/**
 * Small text+color status pill. Reused anywhere an account status needs
 * to be shown (currently Profile). Never color-only — always paired with
 * a readable label.
 */
export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`status-badge status-badge--${status}`}>{STATUS_LABEL[status]}</span>;
}
