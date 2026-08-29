import { apiFetch } from '../config/api';
import type { TransactionItem } from './transactionService';
import type { DisputeItem } from './disputeService';

const LOCAL_STORAGE_KEY = 'digi_wallet_mock_disputes_v1';

function getLocalDisputes(): DisputeItem[] {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveLocalDisputes(list: DisputeItem[]) {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(list));
  } catch (err) {
    console.error(err);
  }
}

export const adminService = {
  async getSystemTransactions(page = 1, limit = 20, search = ''): Promise<TransactionItem[]> {
    const query = search ? `&search=${encodeURIComponent(search)}` : '';
    return await apiFetch<TransactionItem[]>(`/admin/transactions?page=${page}&limit=${limit}${query}`);
  },

  async getSystemDisputes(status = ''): Promise<DisputeItem[]> {
    const local = getLocalDisputes();
    try {
      const query = status ? `?status=${encodeURIComponent(status)}` : '';
      const remote = await apiFetch<DisputeItem[]>(`/admin/disputes${query}`);

      const map = new Map<string, DisputeItem>();
      remote.forEach((d) => map.set(d.id, d));
      local.forEach((d) => {
        if (!map.has(d.id)) {
          map.set(d.id, d);
        }
      });
      return Array.from(map.values());
    } catch (err) {
      if (status) {
        return local.filter((d) => d.status === status);
      }
      return local;
    }
  },

  async executeReversal(disputeId: string, adminNotes = ''): Promise<DisputeItem> {
    try {
      const query = adminNotes ? `?admin_notes=${encodeURIComponent(adminNotes)}` : '';
      return await apiFetch<DisputeItem>(`/admin/disputes/${disputeId}/execute-reversal${query}`, {
        method: 'POST',
      });
    } catch (err) {
      const local = getLocalDisputes();
      const item = local.find((d) => d.id === disputeId);
      if (item) {
        item.status = 'RESOLVED_REVERSED';
        item.admin_notes = adminNotes || 'Reversal executed by Admin';
        item.updated_at = new Date().toISOString();
        saveLocalDisputes(local);
        return item;
      }
      throw err;
    }
  },

  async resolveComplaint(
    disputeId: string,
    decision: 'APPROVE_REVERSAL' | 'REJECT',
    adminNotes = ''
  ): Promise<DisputeItem> {
    try {
      return await apiFetch<DisputeItem>(`/admin/disputes/${disputeId}/resolve`, {
        method: 'POST',
        body: JSON.stringify({
          decision,
          admin_notes: adminNotes,
        }),
      });
    } catch (err) {
      const local = getLocalDisputes();
      const item = local.find((d) => d.id === disputeId);
      if (item) {
        item.status = decision === 'APPROVE_REVERSAL' ? 'RESOLVED_REVERSED' : 'REJECTED';
        item.admin_notes = adminNotes;
        item.updated_at = new Date().toISOString();
        saveLocalDisputes(local);
        return item;
      }
      throw err;
    }
  },

  async makeAdmin(username: string): Promise<{ message: string }> {
    return await apiFetch<{ message: string }>(`/admin/users/${encodeURIComponent(username)}/make-admin`, {
      method: 'POST',
    });
  },
};
