import type { ButtonHTMLAttributes } from 'react';
import { LoadingIndicator } from '../LoadingIndicator/LoadingIndicator';
import './Button.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  /** Shows an inline spinner and swaps the label for `loadingLabel`. */
  isLoading?: boolean;
  loadingLabel?: string;
  fullWidth?: boolean;
}

/**
 * Base button used across auth and account screens. Handles its own
 * loading state so pages don't have to duplicate spinner/disabled logic.
 */
export function Button({
  variant = 'primary',
  isLoading = false,
  loadingLabel = 'Please wait…',
  fullWidth = false,
  disabled,
  className,
  children,
  ...rest
}: ButtonProps) {
  const classes = [
    'button',
    `button--${variant}`,
    fullWidth ? 'button--full-width' : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} disabled={disabled || isLoading} {...rest}>
      {isLoading ? (
        <LoadingIndicator label={loadingLabel} />
      ) : (
        children
      )}
    </button>
  );
}
