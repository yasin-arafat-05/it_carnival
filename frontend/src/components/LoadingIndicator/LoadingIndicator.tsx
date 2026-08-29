import './LoadingIndicator.css';

interface LoadingIndicatorProps {
  /** Visible text explaining what is happening. Always shown, never color-only. */
  label: string;
}

/**
 * Small, calm loading indicator: three softly pulsing dots plus a visible
 * text label. Intentionally subtle — no spinning logos, no big animations.
 */
export function LoadingIndicator({ label }: LoadingIndicatorProps) {
  return (
    <div className="loading-indicator" role="status" aria-live="polite">
      <span className="loading-indicator__dots" aria-hidden="true">
        <span className="loading-indicator__dot" />
        <span className="loading-indicator__dot" />
        <span className="loading-indicator__dot" />
      </span>
      <span className="loading-indicator__label">{label}</span>
    </div>
  );
}
