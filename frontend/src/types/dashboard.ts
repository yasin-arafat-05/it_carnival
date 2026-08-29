import type { AuthUser } from './auth';

/**
 * Dashboard-related types shared between the mock data layer, the mock
 * dashboard service, and the UI. Keeping these separate (like `auth.ts`)
 * means a real API integration can reuse the same shapes later.
 */

export type TransactionDirection = 'sent' | 'received';

export type TransactionStatus = 'completed' | 'pending' | 'failed';

export interface Transaction {
  id: string;
  counterpartyName: string;
  direction: TransactionDirection;
  /** Always a positive magnitude — `direction` conveys sign, not the number. */
  amount: number;
  currency: string;
  /** ISO date-time string. */
  occurredAt: string;
  status: TransactionStatus;
}

export interface DashboardData {
  user: AuthUser;
  balance: number;
  currency: string;
  transactions: Transaction[];
}
