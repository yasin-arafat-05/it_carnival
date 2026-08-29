/**
 * App-entry / session-check service.
 *
 * This is intentionally the ONLY place that decides "where does the app
 * send the user right after launch". Today it's a fixed mock delay with a
 * hardcoded result. Later, this function's body can be swapped for a real
 * call to the backend (e.g. validate a stored token against
 * `GET /auth/me`) WITHOUT any change required in the Splash page — it only
 * ever depends on this module's exported shape.
 */

export type SessionStatus = 'authenticated' | 'unauthenticated';

export interface SessionCheckResult {
  status: SessionStatus;
}

/** Simulated latency for the mock session check, in milliseconds. */
const MOCK_SESSION_CHECK_DELAY_MS = 1200;

/**
 * Mock session check performed on app start.
 *
 * Real implementation later: read a persisted auth token, call the
 * backend to verify it, and resolve 'authenticated' or 'unauthenticated'
 * accordingly.
 *
 * Scope note (Feature 41 only): Login/Registration aren't built yet, so
 * this mock always resolves 'authenticated' after a short simulated delay
 * so the Splash screen has somewhere real to send the user (the temporary
 * Dashboard placeholder). The caller's branching logic (authenticated ->
 * dashboard, unauthenticated -> login) is already written for the real
 * case — only this mock resolution needs to change later.
 */
export function checkSession(): Promise<SessionCheckResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ status: 'authenticated' });
    }, MOCK_SESSION_CHECK_DELAY_MS);
  });
}
