import { apiFetch } from '../config/api';

export interface CreateMoneyRequestPayload {
  payerIdentifier: string;
  amount: number;
  note?: string;
  expiresInHours?: number;
}

export interface MoneyRequestItem {
  id: string;
  requester_id: string;
  payer_id: string;
  requester_name?: string;
  payer_name?: string;
  amount: number;
  note?: string;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'EXPIRED';
  expires_at: string;
  created_at: string;
}

export const moneyRequestService = {
  async createRequest(payload: CreateMoneyRequestPayload): Promise<MoneyRequestItem> {
    return await apiFetch<MoneyRequestItem>('/wallet/request-money', {
      method: 'POST',
      body: JSON.stringify({
        payer_identifier: payload.payerIdentifier,
        amount: payload.amount,
        note: payload.note || '',
        expires_in_hours: payload.expiresInHours || 24,
      }),
    });
  },

  async getIncomingRequests(): Promise<MoneyRequestItem[]> {
    return await apiFetch<MoneyRequestItem[]>('/wallet/requests/incoming');
  },

  async getOutgoingRequests(): Promise<MoneyRequestItem[]> {
    return await apiFetch<MoneyRequestItem[]>('/wallet/requests/outgoing');
  },

  async actionRequest(requestId: string, action: 'ACCEPT' | 'DECLINE'): Promise<MoneyRequestItem> {
    return await apiFetch<MoneyRequestItem>(`/wallet/request-money/${requestId}/action`, {
      method: 'POST',
      body: JSON.stringify({
        action,
        idempotency_key: action === 'ACCEPT' ? `REQ_ACCEPT_${requestId}_${Date.now()}` : undefined,
      }),
    });
  },
};
