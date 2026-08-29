import { TransactionStatusBadge } from '../StatusBadge/TransactionStatusBadge';
import { Skeleton } from '../Skeleton/Skeleton';
import { formatCurrency } from '../../utils/currency';
import type { Transaction } from '../../types/dashboard';
import './TransactionRow.css';

interface TransactionRowProps {
  transaction: Transaction;
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Single read-only transaction row. Receives a transaction object and
 * only formats/displays it — no calculation of amounts or balances.
 */
export function TransactionRow({ transaction }: TransactionRowProps) {
  const isReceived = transaction.direction === 'received';
  const sign = isReceived ? '+' : '−';

  return (
    <li className="transaction-row">
      <div className="transaction-row__main">
        <p className="transaction-row__counterparty">{transaction.counterpartyName}</p>
        <p className="transaction-row__meta">
          <span className={`transaction-row__direction transaction-row__direction--${transaction.direction}`}>
            {isReceived ? 'Received' : 'Sent'}
          </span>
          <span className="transaction-row__dot" aria-hidden="true">
            ·
          </span>
          <span className="transaction-row__date">{formatDateTime(transaction.occurredAt)}</span>
        </p>
      </div>
      <div className="transaction-row__end">
        <p
          className={`transaction-row__amount transaction-row__amount--${transaction.direction}`}
        >
          {sign} {formatCurrency(transaction.amount, transaction.currency)}
        </p>
        <TransactionStatusBadge status={transaction.status} />
      </div>
    </li>
  );
}

/** Skeleton counterpart shown while dashboard data is loading. */
export function TransactionRowSkeleton() {
  return (
    <li className="transaction-row" aria-hidden="true">
      <div className="transaction-row__main">
        <Skeleton width="120px" height="16px" />
        <Skeleton width="90px" height="13px" />
      </div>
      <div className="transaction-row__end">
        <Skeleton width="80px" height="16px" />
        <Skeleton width="64px" height="20px" radius="999px" />
      </div>
    </li>
  );
}
