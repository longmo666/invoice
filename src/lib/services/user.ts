import { apiClient } from '../api/client';
import { User } from './auth';

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UserListParams {
  page?: number;
  page_size?: number;
  search?: string;
}

class UserService {
  async getUsers(params: UserListParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params.search) queryParams.append('search', params.search);

    const query = queryParams.toString();
    return apiClient.get<PageResult<User>>(`/admin/users${query ? `?${query}` : ''}`);
  }

  async getUser(id: number) {
    return apiClient.get<User>(`/admin/users/${id}`);
  }

  async updateStatus(id: number, status: 'active' | 'disabled') {
    return apiClient.patch<User>(`/admin/users/${id}/status?status=${status}`);
  }

  async addQuota(id: number, amount: number) {
    return apiClient.post<User>(`/admin/users/${id}/quota`, { amount });
  }

  async deleteUser(id: number) {
    return apiClient.delete(`/admin/users/${id}`);
  }

  async batchDelete(ids: number[]) {
    return apiClient.post('/admin/users/batch-delete', { ids });
  }
}

export const userService = new UserService();
