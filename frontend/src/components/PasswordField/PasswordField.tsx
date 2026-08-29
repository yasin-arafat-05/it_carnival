import { useId, useState } from 'react';
import type { InputHTMLAttributes } from 'react';
import '../FormField/FormField.css';
import './PasswordField.css';

interface PasswordFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

/**
 * Password input built on the same visual shell as FormField, with a
 * built-in show/hide toggle. Kept separate from FormField because the
 * toggle button needs to live inside the input shell and manage its own
 * local (non-form) state.
 */
export function PasswordField({
  label,
  error,
  hint,
  id,
  className,
  ...rest
}: PasswordFieldProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;
  const [visible, setVisible] = useState(false);

  return (
    <div className={`form-field${className ? ` ${className}` : ''}`}>
      <label className="form-field__label" htmlFor={inputId}>
        {label}
      </label>
      <div className={`form-field__shell${error ? ' form-field__shell--error' : ''}`}>
        <input
          id={inputId}
          type={visible ? 'text' : 'password'}
          className="form-field__input"
          aria-invalid={Boolean(error)}
          aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
          {...rest}
        />
        <button
          type="button"
          className="password-field__toggle"
          onClick={() => setVisible((v) => !v)}
          aria-pressed={visible}
          aria-label={visible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}
        >
          {visible ? 'Hide' : 'Show'}
        </button>
      </div>
      {hint && !error && (
        <p id={hintId} className="form-field__hint">
          {hint}
        </p>
      )}
      <p id={errorId} className="form-field__error" role="alert">
        {error ?? ''}
      </p>
    </div>
  );
}
