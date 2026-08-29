/**
 * Directory/recipient user shape used by the Send Money flow's user
 * search. Deliberately separate from `AuthUser` (the logged-in account)
 * even though the mock demo user could theoretically appear in search
 * results — a real backend will likely expose a narrower "public profile"
 * shape for search than it does for the authenticated user.
 */
export interface RecipientUser {
  id: string;
  name: string;
  /** "@handle" style username, without the leading "@". */
  handle: string;
  email: string;
  phone: string;
}
