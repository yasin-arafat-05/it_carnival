import { MOCK_USER } from './mockAuth';
import type { DashboardData, Transaction } from '../types/dashboard';

/**
 * Single source of truth for mock dashboard data (current user, balance,
 * recent transactions). Nothing outside this file should hardcode a
 * balance or transaction value — `mockDashboardService` reads from here,
 * and the Dashboard page only ever talks to `mockDashboardService`. When
 * the real backend is wired up, this file is deleted and the service
 * starts calling the API instead.
 */

export const MOCK_CURRENCY = 'BDT';

/** Mock available balance. Display-only — nothing in the UI may edit this. */
export const MOCK_BALANCE = 100_000;

export const MOCK_TRANSACTIONS: Transaction[] = [
  {
    id: 'txn_1001',
    counterpartyName: 'Rafiq Islam',
    direction: 'received',
    amount: 5000,
    currency: MOCK_CURRENCY,
    occurredAt: '2026-08-28T14:32:00',
    status: 'completed',
  },
  {
    id: 'txn_1002',
    counterpartyName: 'Green Grocer',
    direction: 'sent',
    amount: 1250.5,
    currency: MOCK_CURRENCY,
    occurredAt: '2026-08-27T09:15:00',
    status: 'completed',
  },
  {
    id: 'txn_1003',
    counterpartyName: 'Nusrat Jahan',
    direction: 'sent',
    amount: 2000,
    currency: MOCK_CURRENCY,
    occurredAt: '2026-08-26T18:47:00',
    status: 'pending',
  },
  {
    id: 'txn_1004',
    counterpartyName: 'Karim Uddin',
    direction: 'received',
    amount: 3200,
    currency: MOCK_CURRENCY,
    occurredAt: '2026-08-25T11:02:00',
    status: 'completed',
  },
  {
    id: 'txn_1005',
    counterpartyName: 'City Electric Co.',
    direction: 'sent',
    amount: 890,
    currency: MOCK_CURRENCY,
    occurredAt: '2026-08-24T20:10:00',
    status: 'failed',
  },
];

export const MOCK_DASHBOARD_DATA: DashboardData = {
  user: MOCK_USER,
  balance: MOCK_BALANCE,
  currency: MOCK_CURRENCY,
  transactions: MOCK_TRANSACTIONS,
};
