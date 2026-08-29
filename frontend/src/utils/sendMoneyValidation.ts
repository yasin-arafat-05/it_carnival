/**
 * Client-side validation helpers for the Send Money flow.
 *
 * IMPORTANT: these checks exist purely for immediate UX feedback (so the
 * user isn't stuck waiting on a network round trip to learn their amount
 * is invalid). They are NOT a security boundary. All of this — amount
 * bounds, self-transfer, receiver existence, authorization, etc. — MUST
 * be re-validated server-side by the backend regardless of what the
 * client already checked, since client-side validation can always be
 * bypassed (devtools, direct API calls, modified clients, etc.).
 */

const AMOUNT_PATTERN = /^\d+(\.\d{1,2})?$/;

/** Parses a raw amount string into a finite number, or `undefined` if it isn't one. */
export function parseAmount(rawValue: string): number | undefined {
  const trimmed = rawValue.trim();
  if (!trimmed || !AMOUNT_PATTERN.test(trimmed)) {
    return undefined;
  }
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : undefined;
}

/**
 * Validates the amount field.
 * - Required, numeric (up to 2 decimal places).
 * - Must be greater than zero.
 * - Must not exceed the sender's mock available balance.
 */
export function validateAmount(rawValue: string, availableBalance: number): string | undefined {
  const trimmed = rawValue.trim();
  if (!trimmed) {
    return 'Enter an amount.';
  }
  const amount = parseAmount(trimmed);
  if (amount === undefined) {
    return 'Enter a valid numeric amount.';
  }
  if (amount <= 0) {
    return 'Amount must be greater than zero.';
  }
  if (amount > availableBalance) {
    return "Amount exceeds your available balance.";
  }
  return undefined;
}

/** A receiver must be selected before the send form can be submitted. */
export function validateReceiverSelected(receiverId: string | undefined): string | undefined {
  if (!receiverId) {
    return 'Select someone to send money to.';
  }
  return undefined;
}

/** Blocks sending money to your own account. */
export function validateNotSelfTransfer(
  receiverId: string,
  currentUserId: string,
): string | undefined {
  if (receiverId === currentUserId) {
    return "You can't send money to yourself.";
  }
  return undefined;
}

const MAX_NOTE_LENGTH = 140;

/** Optional field — only rejected if it's unreasonably long. */
export function validateNote(value: string): string | undefined {
  if (value.trim().length > MAX_NOTE_LENGTH) {
    return `Note must be ${MAX_NOTE_LENGTH} characters or fewer.`;
  }
  return undefined;
}
