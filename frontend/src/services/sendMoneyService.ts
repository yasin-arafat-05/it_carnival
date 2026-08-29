import { generateMockTransactionReference } from '../utils/transactionReference';
import type { AppErrorCode } from '../types/errors';

/**
 * Mock "send money" submission service.
 *
 * This is the ONLY module the Send Money screen talks to for submitting a
 * transfer. It simulates network latency and a demonstrable
 * success/failure outcome. Later, `sendMoney()` can be reimplemented to
 * call the real backend (e.g. POST /transactions/send) with an identical
 * return shape — no page/component changes required. The failure shape
 * carries a backend-style `code` (see `types/errors.ts`) so the UI's
 * `ErrorBanner` can map it to a friendly message the same way it will for
 * real API error responses.
 *
 * IMPORTANT — validation: this mock performs no real validation. Every
 * check done in the UI (amount limits, self-transfer, etc.) is a
 * client-side UX convenience only — the real backend MUST re-validate all
 * of it (receiver exists, amount > 0, amount <= available balance, no
 * self-transfer, authorization, etc.) independently, since client-side
 * checks can always be bypassed.
 *
 * IMPORTANT — idempotency: tapping "Confirm" twice (double-tap, slow
 * network + impatient user, etc.) must never create two transfers. Today
 * the UI-only protects against this by disabling the Confirm button and
 * ignoring repeat calls while a request is in flight (see SendMoneyPage).
 * That is NOT sufficient on its own — the real backend MUST generate/accept
 * a server-side idempotency key (e.g. a client-generated request ID sent
 * with the request and deduplicated server-side) so that retried or
 * duplicate network requests for the same transfer intent are only ever
 * applied once, regardless of what the client does.
 */

export interface SendMoneyPayload {
  receiverId: string;
  amount: number;
  note: string;
}

export interface SendMoneySuccess {
  ok: true;
  transactionId: string;
  /** Mock, display-only reference — see `generateMockTransactionReference`. */
  reference: string;
}

export interface SendMoneyFailure {
  ok: false;
  /** Backend-style error code, when the failure matches a known case. */
  code?: AppErrorCode;
  /** Human-readable fallback, used when `code` is absent. */
  message: string;
}

export type SendMoneyResult = SendMoneySuccess | SendMoneyFailure;

const MOCK_SEND_DELAY_MS = 1200;

/**
 * Demo-only, clearly identifiable way to force a specific result without
 * relying on randomness — makes every Transfer Result / error state easy
 * to reach on demand. Typing one of these words (case insensitive)
 * anywhere in the optional note forces the matching outcome; anything
 * else succeeds. This has no equivalent in a real backend and must be
 * removed once real transfer processing exists.
 */
const MOCK_FORCE_KEYWORDS: Record<string, AppErrorCode> = {
  insufficient: 'insufficient_balance',
  suspended: 'account_suspended',
  notfound: 'receiver_not_found',
  invalidamount: 'invalid_amount',
};
const MOCK_GENERIC_FAILURE_KEYWORD = 'fail';
const MOCK_GENERIC_FAILURE_MESSAGE = 'The transfer could not be completed. Please try again.';

let mockTransactionSeq = 5000;

export const mockSendMoneyService = {
  sendMoney(payload: SendMoneyPayload): Promise<SendMoneyResult> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const normalizedNote = payload.note.toLowerCase();

        const forcedCode = Object.entries(MOCK_FORCE_KEYWORDS).find(([keyword]) =>
          normalizedNote.includes(keyword),
        )?.[1];

        if (forcedCode) {
          resolve({ ok: false, code: forcedCode, message: MOCK_GENERIC_FAILURE_MESSAGE });
          return;
        }

        if (normalizedNote.includes(MOCK_GENERIC_FAILURE_KEYWORD)) {
          resolve({ ok: false, message: MOCK_GENERIC_FAILURE_MESSAGE });
          return;
        }

        mockTransactionSeq += 1;
        resolve({
          ok: true,
          transactionId: `txn_${mockTransactionSeq}`,
          reference: generateMockTransactionReference(),
        });
      }, MOCK_SEND_DELAY_MS);
    });
  },
};
