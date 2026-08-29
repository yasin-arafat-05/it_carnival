import { apiFetch } from '../config/api';
import type { DashboardData } from '../types/dashboard';

/**
 * Dashboard Service calling GET /users/me and GET /wallet/dashboard
 */
export const dashboardService = {
  async getDashboardData(): Promise<DashboardData> {
    const userMe = await apiFetch<any>('/users/me');
    const dashboard = await apiFetch<any>('/wallet/dashboard');

    const currentUser = {
      id: userMe.id,
      name: userMe.full_name,
      username: userMe.username,
      email: userMe.email,
      phone: userMe.phone_number,
      role: userMe.role || 'USER',
      accountStatus: (userMe.account_status || 'ACTIVE').toLowerCase() as any,
      createdAt: userMe.created_at,
    };

    const myAccountId = dashboard.account?.id;
    const rawTxs = dashboard.recent_transactions || [];

    const transactions = rawTxs.map((tx: any) => {
      const isSent = tx.sender_account_id === myAccountId;
      const counterpartyName = isSent
        ? (tx.receiver_username || 'Recipient')
        : (tx.sender_username || 'Initial Credit / System');

      return {
        id: tx.id,
        counterpartyName,
        direction: isSent ? ('sent' as const) : ('received' as const),
        amount: Number(tx.amount),
        currency: tx.currency || 'BDT',
        occurredAt: tx.created_at,
        status: (tx.status || 'completed').toLowerCase() as any,
      };
    });

    return {
      user: currentUser,
      balance: Number(dashboard.account?.balance || userMe.account?.balance || 0),
      currency: dashboard.account?.currency || 'BDT',
      transactions,
    };
  },
};

export const mockDashboardService = dashboardService;
