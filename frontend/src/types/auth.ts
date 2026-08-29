/**
 * Auth-related types shared between the mock data layer, the mock auth
 * service, and the UI. Keeping these separate from both means the real
 * API integration can reuse the same shapes.
 */

export interface LoginCredentials {
  /** Raw value from the "email or username" field, untrimmed. */
  identifier: string;
  password: string;
}

export type AccountStatus = 'active' | 'suspended';

export interface AuthUser {
  id: string;
  name: string;
  username: string;
  email: string;
  /** Optional profile fields — present on the mock demo user for Feature 4/54. */
  phone?: string;
  role?: string;
  accountStatus?: AccountStatus;
  /** ISO date string. */
  createdAt?: string;
}

export interface LoginSuccess {
  ok: true;
  user: AuthUser;
}

export interface LoginFailure {
  ok: false;
  /** Human-readable message, safe to show directly in the UI. */
  message: string;
}

export type LoginResult = LoginSuccess | LoginFailure;

export interface RegisterCredentials {
  fullName: string;
  email: string;
  username: string;
  password: string;
}

export interface RegisterSuccess {
  ok: true;
  user: AuthUser;
  /** Mock starting balance (in BDT) shown on the success screen. */
  startingBalance: number;
}

export interface RegisterFailure {
  ok: false;
  /** Human-readable message, safe to show directly in the UI. */
  message: string;
}

export type RegisterResult = RegisterSuccess | RegisterFailure;
