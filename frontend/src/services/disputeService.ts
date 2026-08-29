import { apiFetch } from '../config/api';

export interface DisputeItem {
  id: string;
  transaction_id?: string;
  transaction_reference?: string;
  sender_id?: string;
  receiver_id?: string;
  sender_username?: string;
  receiver_username?: string;
  amount: number;
  dispute_type: 'FALSE_TRANSACTION' | 'FORMAL_COMPLAINT';
  status:
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
  reason: string;
  receiver_notes?: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
}

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

export const disputeService = {
  async requestFalseTransactionReversal(transactionReference: string, reason: string): Promise<DisputeItem> {
    try {
      return await apiFetch<DisputeItem>('/wallet/disputes/false-transaction', {
        method: 'POST',
        body: JSON.stringify({
          transaction_reference: transactionReference,
          reason,
        }),
      });
    } catch (err) {
      console.warn('API call failed, saving dispute to local mock state:', err);
      const disputes = getLocalDisputes();
      const existing = disputes.find((d) => d.transaction_reference === transactionReference);
      if (existing) {
        throw new Error('A dispute has already been filed for this transaction.');
      }
      const newDispute: DisputeItem = {
        id: `disp_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        transaction_reference: transactionReference,
        amount: 2500,
        dispute_type: 'FALSE_TRANSACTION',
        status: 'PENDING_RECEIVER_CONFIRMATION',
        reason,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      disputes.unshift(newDispute);
      saveLocalDisputes(disputes);
      return newDispute;
    }
  },

  async getPendingConfirmations(): Promise<DisputeItem[]> {
    try {
      return await apiFetch<DisputeItem[]>('/wallet/disputes/pending-confirmations');
    } catch (err) {
      return getLocalDisputes().filter((d) => d.status === 'PENDING_RECEIVER_CONFIRMATION');
    }
  },

  async receiverConfirm(disputeId: string, action: 'CONFIRM' | 'DENY', notes?: string): Promise<DisputeItem> {
    try {
      return await apiFetch<DisputeItem>(`/wallet/disputes/${disputeId}/receiver-confirm`, {
        method: 'POST',
        body: JSON.stringify({
          action,
          notes: notes || '',
        }),
      });
    } catch (err) {
      const disputes = getLocalDisputes();
      const item = disputes.find((d) => d.id === disputeId);
      if (!item) throw new Error('Dispute not found.');

      if (action === 'CONFIRM') {
        item.status = 'CONFIRMED_BY_RECEIVER';
      } else {
        item.status = 'REJECTED';
      }
      item.receiver_notes = notes;
      item.updated_at = new Date().toISOString();
      saveLocalDisputes(disputes);
      return item;
    }
  },

  async fileComplaint(transactionReference: string, reason: string): Promise<DisputeItem> {
    try {
      return await apiFetch<DisputeItem>('/wallet/disputes/file-complaint', {
        method: 'POST',
        body: JSON.stringify({
          transaction_reference: transactionReference,
          reason,
        }),
      });
    } catch (err) {
      const disputes = getLocalDisputes();
      const newDispute: DisputeItem = {
        id: `complaint_${Date.now()}`,
        transaction_reference: transactionReference,
        amount: 1000,
        dispute_type: 'FORMAL_COMPLAINT',
        status: 'UNDER_INVESTIGATION',
        reason,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      disputes.unshift(newDispute);
      saveLocalDisputes(disputes);
      return newDispute;
    }
  },

  async getMyDisputes(): Promise<DisputeItem[]> {
    try {
      const remote = await apiFetch<DisputeItem[]>('/wallet/disputes/my-disputes');
      return remote;
    } catch (err) {
      return getLocalDisputes();
    }
  },

  async getDisputeForTransaction(transactionReference: string): Promise<DisputeItem | undefined> {
    try {
      const list = await this.getMyDisputes();
      return list.find((d) => d.transaction_reference === transactionReference);
    } catch {
      return undefined;
    }
  },
};

export const mockDisputeService = disputeService;
