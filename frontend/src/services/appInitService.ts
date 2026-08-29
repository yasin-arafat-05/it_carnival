import { apiFetch, getAuthToken, removeAuthToken } from '../config/api';

export type SessionStatus = 'authenticated' | 'unauthenticated';

export interface SessionCheckResult {
  status: SessionStatus;
}

/**
 * Real session verification performed on app startup against GET /users/me.
 */
export async function checkSession(): Promise<SessionCheckResult> {
  const token = getAuthToken();
  if (!token) {
    return { status: 'unauthenticated' };
  }

  try {
    await apiFetch('/users/me');
    return { status: 'authenticated' };
  } catch (err) {
    removeAuthToken();
    return { status: 'unauthenticated' };
  }
}
