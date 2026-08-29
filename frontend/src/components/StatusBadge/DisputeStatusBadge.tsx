import './StatusBadge.css';

export type DisputeStatusType =
  | 'PENDING_RECEIVER_CONFIRMATION'
  | 'DISPUTE_PENDING'
  | 'RECEIVER_PENDING'
  | 'CONFIRMED_BY_RECEIVER'
  | 'RECEIVER_CONFIRMED'
  | 'UNDER_INVESTIGATION'
  | 'REJECTED'
  | 'REJECTED_BY_RECEIVER'
  | 'REFUND_APPROVED'
  | 'RESOLVED_REVERSED'
  | 'REFUND_COMPLETED';

interface DisputeStatusBadgeProps {
  status: DisputeStatusType | string;
}

const DISPUTE_STATUS_MAP: Record<string, { label: string; modifierClass: string }> = {
  PENDING_RECEIVER_CONFIRMATION: { label: 'Receiver Pending', modifierClass: 'receiver-pending' },
  DISPUTE_PENDING: { label: 'Dispute Pending', modifierClass: 'dispute-pending' },
  RECEIVER_PENDING: { label: 'Receiver Pending', modifierClass: 'receiver-pending' },
  CONFIRMED_BY_RECEIVER: { label: 'Receiver Confirmed', modifierClass: 'receiver-confirmed' },
  RECEIVER_CONFIRMED: { label: 'Receiver Confirmed', modifierClass: 'receiver-confirmed' },
  UNDER_INVESTIGATION: { label: 'Under Investigation', modifierClass: 'under-investigation' },
  REJECTED: { label: 'Rejected', modifierClass: 'dispute-rejected' },
  REJECTED_BY_RECEIVER: { label: 'Rejected by Receiver', modifierClass: 'dispute-rejected' },
  REFUND_APPROVED: { label: 'Refund Approved', modifierClass: 'refund-approved' },
  RESOLVED_REVERSED: { label: 'Refund Completed', modifierClass: 'refund-completed' },
  REFUND_COMPLETED: { label: 'Refund Completed', modifierClass: 'refund-completed' },
};

export function DisputeStatusBadge({ status }: DisputeStatusBadgeProps) {
  const upper = (status || '').toUpperCase();
  const config = DISPUTE_STATUS_MAP[upper] || {
    label: upper.replace(/_/g, ' '),
    modifierClass: 'dispute-pending',
  };

  return (
    <span className={`status-badge status-badge--${config.modifierClass}`}>
      {config.label}
    </span>
  );
}
