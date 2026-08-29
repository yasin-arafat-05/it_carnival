import type { InputHTMLAttributes, ReactNode } from 'react';
import { useId } from 'react';
import './FormField.css';

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  /** Inline validation message. Reserves layout space even when absent. */
  error?: string;
  hint?: string;
  /** Optional trailing content inside the input shell, e.g. a show/hide toggle. */
  endAdornment?: ReactNode;
}

/**
 * Labeled text input with a real <label>, an inline error slot that
 * reserves space (so validation messages never shift layout), and
 * standard aria wiring for accessibility.
 */
export function FormField({
  label,
  error,
  hint,
  endAdornment,
  id,
  className,
  ...rest
}: FormFieldProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <div className={`form-field${className ? ` ${className}` : ''}`}>
      <label className="form-field__label" htmlFor={inputId}>
        {label}
      </label>
      <div className={`form-field__shell${error ? ' form-field__shell--error' : ''}`}>
        <input
          id={inputId}
          className="form-field__input"
          aria-invalid={Boolean(error)}
          aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
          {...rest}
        />
        {endAdornment}
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
