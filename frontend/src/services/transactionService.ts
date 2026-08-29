import { apiFetch } from '../config/api';

export interface TransactionItem {
  id: string;
  reference_id: string;
  sender_account_id?: string;
  receiver_account_id: string;
  sender_username?: string;
  receiver_username?: string;
  amount: number;
  currency: string;
  transaction_type: string;
  status: string;
  idempotency_key?: string;
  note?: string;
  created_at: string;
}

export interface LedgerItem {
  id: string;
  transaction_id: string;
  account_id: string;
  entry_type: 'DEBIT' | 'CREDIT';
  amount: number;
  balance_after: number;
  created_at: string;
}

export const transactionService = {
  async getTransactions(page = 1, limit = 20): Promise<TransactionItem[]> {
    return await apiFetch<TransactionItem[]>(`/wallet/transactions?page=${page}&limit=${limit}`);
  },

  async getTransactionByReference(referenceId: string): Promise<TransactionItem> {
    return await apiFetch<TransactionItem>(`/wallet/transactions/${encodeURIComponent(referenceId)}`);
  },

  async getLedgerEntries(page = 1, limit = 20): Promise<LedgerItem[]> {
    return await apiFetch<LedgerItem[]>(`/wallet/ledger?page=${page}&limit=${limit}`);
  },
};
