import {
  MOCK_STARTING_BALANCE,
  MOCK_TAKEN_USERNAMES,
  MOCK_USER,
  MOCK_VALID_CREDENTIALS,
} from '../data/mockAuth';
import type {
  AuthUser,
  LoginCredentials,
  LoginResult,
  RegisterCredentials,
  RegisterResult,
} from '../types/auth';

/**
 * Mock authentication service.
 *
 * This is the ONLY module the UI talks to for logging in. It currently
 * simulates network latency and checks against hardcoded mock
 * credentials. Later, `login()` can be reimplemented to call the real
 * backend (e.g. POST /token) and this file's exported shape
 * (`mockAuthService.login`) can simply become `authService.login` with
 * an identical signature — no page/component changes required.
 */

const MOCK_LOGIN_DELAY_MS = 900;
const MOCK_REGISTER_DELAY_MS = 900;

let mockRegisteredId = 2000;

function normalize(value: string): string {
  return value.trim().toLowerCase();
}

export const mockAuthService = {
  login(credentials: LoginCredentials): Promise<LoginResult> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const identifierMatches =
          normalize(credentials.identifier) === normalize(MOCK_VALID_CREDENTIALS.identifier) ||
          normalize(credentials.identifier) === normalize(MOCK_USER.username);
        const passwordMatches = credentials.password === MOCK_VALID_CREDENTIALS.password;

        if (identifierMatches && passwordMatches) {
          resolve({ ok: true, user: MOCK_USER });
          return;
        }

        resolve({
          ok: false,
          message: "The email or username and password don't match.",
        });
      }, MOCK_LOGIN_DELAY_MS);
    });
  },

  /**
   * Mock registration. Only rejects hardcoded taken usernames (see
   * `MOCK_TAKEN_USERNAMES`) — everything else "succeeds" and returns a
   * freshly minted mock user with the flat mock starting balance. Never
   * touches a real backend, database, or session.
   */
  register(credentials: RegisterCredentials): Promise<RegisterResult> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const usernameTaken = MOCK_TAKEN_USERNAMES.some(
          (taken) => normalize(taken) === normalize(credentials.username),
        );

        if (usernameTaken) {
          resolve({ ok: false, message: 'That username is already taken.' });
          return;
        }

        mockRegisteredId += 1;
        const user: AuthUser = {
          id: `user_${mockRegisteredId}`,
          name: credentials.fullName.trim(),
          username: credentials.username.trim(),
          email: credentials.email.trim(),
        };

        resolve({ ok: true, user, startingBalance: MOCK_STARTING_BALANCE });
      }, MOCK_REGISTER_DELAY_MS);
    });
  },
};
