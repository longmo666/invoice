import { apiClient } from '../api/client';

export interface User {
  id: number;
  username: string;
  role: 'user' | 'admin';
  status: 'active' | 'disabled';
  remaining_quota: number;
  used_quota: number;
  created_at: string;
  last_login_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

class AuthService {
  async register(data: RegisterRequest) {
    const response = await apiClient.post<TokenResponse>('/auth/register', data);
    if (response.success && response.data) {
      this.setToken(response.data.access_token);
    }
    return response;
  }

  async login(data: LoginRequest) {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    if (response.success && response.data) {
      this.setToken(response.data.access_token);
    }
    return response;
  }

  async adminLogin(data: LoginRequest) {
    const response = await apiClient.post<TokenResponse>('/auth/admin-login', data);
    if (response.success && response.data) {
      this.setToken(response.data.access_token);
    }
    return response;
  }

  async getMe() {
    return apiClient.get<User>('/auth/me');
  }

  async logout() {
    this.clearToken();
    return apiClient.post('/auth/logout');
  }

  async changePassword(currentPassword: string, newPassword: string) {
    return apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  setToken(token: string) {
    localStorage.setItem('access_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  clearToken() {
    localStorage.removeItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
