import './ErrorMessage.css';

interface ErrorMessageProps {
  message: string;
}

/**
 * Inline, non-blocking error banner for form-level failures (e.g. "invalid
 * credentials") as opposed to per-field validation messages. Always
 * paired with visible text and an icon — never color alone.
 */
export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="error-message" role="alert">
      <span className="error-message__icon" aria-hidden="true">
        ⚠
      </span>
      <span>{message}</span>
    </div>
  );
}
