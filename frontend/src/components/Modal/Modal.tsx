import { useEffect, useId } from 'react';
import type { ReactNode } from 'react';
import './Modal.css';

interface ModalProps {
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  onClose: () => void;
  /** When true, Escape and backdrop-click are ignored (e.g. mid-submit). */
  isDismissDisabled?: boolean;
}

/**
 * Small, generic confirmation dialog. Purely presentational — the caller
 * owns all state (open/closed, what's inside, what the footer buttons do).
 * Built for the Send Money confirmation step but intentionally not
 * Send-Money-specific, so later flows (Request Money, etc.) can reuse it.
 */
export function Modal({ title, children, footer, onClose, isDismissDisabled = false }: ModalProps) {
  const titleId = useId();

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape' && !isDismissDisabled) {
        onClose();
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose, isDismissDisabled]);

  return (
    <div
      className="modal-overlay"
      onMouseDown={() => {
        if (!isDismissDisabled) onClose();
      }}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <h2 id={titleId} className="modal__title">
          {title}
        </h2>
        <div className="modal__body">{children}</div>
        {footer && <div className="modal__footer">{footer}</div>}
      </div>
    </div>
  );
}
