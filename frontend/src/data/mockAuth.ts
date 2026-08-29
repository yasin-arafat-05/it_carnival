import type { AuthUser } from '../types/auth';

/**
 * Single source of truth for mock authentication data.
 *
 * Nothing outside this file should hardcode a user's credentials or
 * profile fields — `mockAuthService` reads from here, and UI components
 * only ever talk to `mockAuthService`. When the real backend is wired up,
 * this file is deleted and the service starts calling the API instead.
 */

export const MOCK_USER: AuthUser = {
  id: 'user_1001',
  name: 'Amina Rahman',
  username: 'amina.rahman',
  email: 'amina@itcarnival.com',
  phone: '+880 1711-234567',
  accountStatus: 'active',
  createdAt: '2024-03-12',
};

/** The only combination that mock-authenticates successfully. */
export const MOCK_VALID_CREDENTIALS = {
  identifier: MOCK_USER.email,
  password: 'Wallet123!',
};

/**
 * A realistic "wrong password" for the demo account — used to make sure
 * the login form's invalid-credentials path is easy to demo deliberately.
 */
export const MOCK_BAD_PASSWORD = 'WrongPassword1!';

/** Usernames that always fail registration with "already taken". */
export const MOCK_TAKEN_USERNAMES = ['admin'];

/** Mock starting balance (BDT) assigned to every newly "registered" account. */
export const MOCK_STARTING_BALANCE = 100_000;
