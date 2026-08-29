import type { AppErrorCode } from '../../types/errors';
import './ErrorBanner.css';

interface ErrorBannerProps {
  /** A known backend error code. Takes priority over `message` when both are given. */
  code?: AppErrorCode;
  /** Fallback/custom text, used when `code` is absent or unrecognized. */
  message?: string;
}

/**
 * Feature 35 — Error Handling UI.
 *
 * Shared, reusable error banner that maps a backend-style error *code* to
 * a distinct, user-friendly message — so the UI never has to hardcode
 * "if amount too big show X" logic per screen. Designed so a future
 * backend response's error code can be passed straight through via
 * `code` with no translation step; `message` remains available for
 * screens that only have free-text errors (e.g. network failures).
 *
 * Frontend-only: this component does not call any API and does not know
 * *when* an error code applies — callers decide that from a (currently
 * mocked) service result.
 */
const ERROR_MESSAGES: Record<AppErrorCode, string> = {
  insufficient_balance: "You don't have enough balance to complete this transfer.",
  receiver_not_found: "We couldn't find that recipient. Please check and try again.",
  account_suspended: 'Your account is suspended. Contact support for help.',
  invalid_amount: 'Enter a valid amount greater than zero.',
};

export function ErrorBanner({ code, message }: ErrorBannerProps) {
  const text = (code && ERROR_MESSAGES[code]) || message;

  if (!text) {
    return null;
  }

  return (
    <div className="error-banner" role="alert">
      <span className="error-banner__icon" aria-hidden="true">
        ⚠
      </span>
      <span>{text}</span>
    </div>
  );
}
