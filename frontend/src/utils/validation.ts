/**
 * Small, framework-agnostic validation helpers shared across auth forms.
 * Plain functions on purpose — easy to unit test and reuse from
 * Login/Register without pulling in a form library.
 */

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** True if the value "looks like" an email attempt (contains an @). */
export function looksLikeEmail(value: string): boolean {
  return value.includes('@');
}

export function isValidEmail(value: string): boolean {
  return EMAIL_PATTERN.test(value.trim());
}

/**
 * Validates the Login screen's "email or username" field.
 * - Required.
 * - If it looks like an email attempt, it must be a well-formed email.
 * - Otherwise treated as a username with a minimal length check.
 */
export function validateLoginIdentifier(value: string): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) {
    return 'Enter your email or username.';
  }
  if (looksLikeEmail(trimmed) && !isValidEmail(trimmed)) {
    return 'Enter a valid email address.';
  }
  if (!looksLikeEmail(trimmed) && trimmed.length < 3) {
    return 'Enter a valid email or username.';
  }
  return undefined;
}

export function validateLoginPassword(value: string): string | undefined {
  if (!value) {
    return 'Enter your password.';
  }
  return undefined;
}

const USERNAME_PATTERN = /^[a-zA-Z0-9_.]+$/;

export function validateFullName(value: string): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) {
    return 'Enter your full name.';
  }
  if (trimmed.length < 2) {
    return 'Enter your full name.';
  }
  return undefined;
}

export function validateRegisterEmail(value: string): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) {
    return 'Enter your email address.';
  }
  if (!isValidEmail(trimmed)) {
    return 'Enter a valid email address.';
  }
  return undefined;
}

/**
 * Validates the Registration screen's username field.
 * - Required, 3-20 characters.
 * - Letters, numbers, underscore, and period only.
 * - Hardcoded taken usernames are rejected with a friendly message.
 */
export function validateUsername(
  value: string,
  takenUsernames: readonly string[] = [],
): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) {
    return 'Choose a username.';
  }
  if (trimmed.length < 3 || trimmed.length > 20) {
    return 'Username must be 3–20 characters.';
  }
  if (!USERNAME_PATTERN.test(trimmed)) {
    return 'Username can only contain letters, numbers, periods, and underscores.';
  }
  if (takenUsernames.some((taken) => taken.toLowerCase() === trimmed.toLowerCase())) {
    return 'That username is already taken.';
  }
  return undefined;
}

export function validateNewPassword(value: string): string | undefined {
  if (!value) {
    return 'Create a password.';
  }
  if (value.length < 8) {
    return 'Password must be at least 8 characters.';
  }
  return undefined;
}

export function validateConfirmPassword(password: string, confirm: string): string | undefined {
  if (!confirm) {
    return 'Confirm your password.';
  }
  if (confirm !== password) {
    return "Passwords don't match.";
  }
  return undefined;
}

export type PasswordStrength = 'weak' | 'fair' | 'strong';

/**
 * Simple, transparent password-strength heuristic — not a security
 * measure, just a helpful visual nudge. Scores on length and character
 * variety (lowercase, uppercase, digit, symbol).
 */
export function getPasswordStrength(value: string): PasswordStrength | undefined {
  if (!value) {
    return undefined;
  }
  let score = 0;
  if (value.length >= 8) score += 1;
  if (value.length >= 12) score += 1;
  if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1;
  if (/\d/.test(value)) score += 1;
  if (/[^a-zA-Z0-9]/.test(value)) score += 1;

  if (score <= 2) return 'weak';
  if (score <= 3) return 'fair';
  return 'strong';
}
