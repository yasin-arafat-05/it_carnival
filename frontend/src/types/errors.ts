/**
 * Shared, backend-agnostic error codes for user-facing failures across the
 * wallet flows (Send Money today; Request Money / transaction history
 * later). Kept separate from any single feature's types so a real backend
 * can return one of these exact codes (e.g. in a JSON error body's
 * `code` field) and the UI needs no translation layer beyond
 * `ErrorBanner`.
 */
export type AppErrorCode =
  | 'insufficient_balance'
  | 'receiver_not_found'
  | 'account_suspended'
  | 'invalid_amount';
