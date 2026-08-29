import { MOCK_USERS } from '../data/mockUsers';
import type { RecipientUser } from '../types/user';

/**
 * Mock user-directory service.
 *
 * This is the ONLY module the Send Money flow talks to for recipient
 * lookup/search. It simulates network latency against the shared mock
 * user list. Later, `searchUsers`/`getUserById` can be reimplemented to
 * call a real backend (e.g. GET /users?q=) with identical return shapes —
 * no page/component changes required.
 */

const MOCK_SEARCH_DELAY_MS = 500;
const MOCK_LOOKUP_DELAY_MS = 400;

function normalize(value: string): string {
  return value.trim().toLowerCase();
}

export const mockUserService = {
  /** Empty/whitespace query returns the full mock directory. */
  searchUsers(query: string): Promise<RecipientUser[]> {
    const needle = normalize(query);

    return new Promise((resolve) => {
      setTimeout(() => {
        if (!needle) {
          resolve(MOCK_USERS);
          return;
        }

        const results = MOCK_USERS.filter((user) =>
          [user.name, user.handle, user.email, user.phone].some((field) =>
            normalize(field).includes(needle),
          ),
        );
        resolve(results);
      }, MOCK_SEARCH_DELAY_MS);
    });
  },

  getUserById(id: string): Promise<RecipientUser | undefined> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_USERS.find((user) => user.id === id));
      }, MOCK_LOOKUP_DELAY_MS);
    });
  },
};
