import { apiFetch } from '../config/api';
import type { AppErrorCode } from '../types/errors';

export interface SendMoneyPayload {
  receiverId: string;
  amount: number;
  note: string;
}

export interface SendMoneySuccess {
  ok: true;
  transactionId: string;
  reference: string;
}

export interface SendMoneyFailure {
  ok: false;
  code?: AppErrorCode;
  message: string;
}

export type SendMoneyResult = SendMoneySuccess | SendMoneyFailure;

export const sendMoneyService = {
  async sendMoney(payload: SendMoneyPayload): Promise<SendMoneyResult> {
    try {
      const data = await apiFetch<any>('/wallet/transfer', {
        method: 'POST',
        body: JSON.stringify({
          receiver_identifier: payload.receiverId,
          amount: payload.amount,
          note: payload.note || '',
          idempotency_key: `SEND_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        }),
      });

      return {
        ok: true,
        transactionId: data.id,
        reference: data.reference_id,
      };
    } catch (err: any) {
      const errMsg = err.message || 'Transfer failed';
      let code: AppErrorCode | undefined = undefined;

      if (errMsg.toLowerCase().includes('insufficient')) {
        code = 'insufficient_balance';
      } else if (errMsg.toLowerCase().includes('not found')) {
        code = 'receiver_not_found';
      } else if (errMsg.toLowerCase().includes('suspended')) {
        code = 'account_suspended';
      }

      return {
        ok: false,
        code,
        message: errMsg,
      };
    }
  },
};

export const mockSendMoneyService = sendMoneyService;
