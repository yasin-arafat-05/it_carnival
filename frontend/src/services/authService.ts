import { apiFetch, setAuthToken, removeAuthToken } from '../config/api';
import type {
  AuthUser,
  LoginCredentials,
  LoginResult,
  RegisterCredentials,
  RegisterResult,
} from '../types/auth';

/**
 * Authentication Service connected to FastAPI Backend API endpoints:
 * - POST /auth/login
 * - POST /auth/signup
 */

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResult> {
    try {
      const data = await apiFetch<any>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          identifier: credentials.identifier,
          password: credentials.password,
        }),
      });

      if (data.access_token) {
        setAuthToken(data.access_token);
        const user = data.user;
        const authUser: AuthUser = {
          id: user.id,
          name: user.full_name,
          username: user.username,
          email: user.email,
          phone: user.phone_number,
          accountStatus: (user.account_status || 'ACTIVE').toLowerCase() as any,
          createdAt: user.created_at,
        };
        return { ok: true, user: authUser };
      }
      return { ok: false, message: 'Invalid response received from authentication server.' };
    } catch (err: any) {
      return { ok: false, message: err.message || 'Login failed. Please check your credentials.' };
    }
  },

  async register(credentials: RegisterCredentials): Promise<RegisterResult> {
    try {
      const phone = (credentials as any).phoneNumber || `017${Math.floor(10000000 + Math.random() * 90000000)}`;
      const payload = {
        full_name: credentials.fullName,
        username: credentials.username,
        phone_number: phone,
        email: credentials.email,
        password: credentials.password,
      };

      const data = await apiFetch<any>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      // Automatically log in after registration
      const loginRes = await this.login({
        identifier: credentials.username,
        password: credentials.password,
      });

      if (loginRes.ok) {
        const startingBalance = data.account?.balance ? Number(data.account.balance) : 100000;
        return {
          ok: true,
          user: loginRes.user,
          startingBalance,
        };
      }

      return { ok: false, message: 'Account registered successfully, but automatic login failed.' };
    } catch (err: any) {
      return { ok: false, message: err.message || 'Registration failed.' };
    }
  },

  logout(): void {
    removeAuthToken();
  },
};

export const mockAuthService = authService;
