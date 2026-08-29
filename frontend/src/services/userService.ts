import { apiFetch } from '../config/api';
import type { RecipientUser } from '../types/user';

/**
 * User Service connected to GET /users/search API endpoint.
 */
export const userService = {
  async searchUsers(query: string): Promise<RecipientUser[]> {
    const searchTerm = query ? query.trim() : '';
    try {
      const data = await apiFetch<any[]>(`/users/search?query=${encodeURIComponent(searchTerm)}`);
      return data.map((u: any) => ({
        id: u.id,
        name: u.full_name,
        handle: u.username,
        email: u.email,
        phone: u.phone_number,
      }));
    } catch (err) {
      console.error('Error searching users:', err);
      return [];
    }
  },

  async getUserById(id: string): Promise<RecipientUser | undefined> {
    try {
      const users = await this.searchUsers(id);
      const match = users.find((user) => user.id === id || user.handle === id || user.email === id);
      if (match) return match;
      if (users.length > 0) return users[0];

      const defaultList = await this.searchUsers('');
      return defaultList.find((user) => user.id === id || user.handle === id || user.email === id);
    } catch (err) {
      return undefined;
    }
  },
};

export const mockUserService = userService;
