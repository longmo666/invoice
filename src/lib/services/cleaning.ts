import { apiClient } from '../api/client';

export interface CleaningTask {
  id: number;
  user_id: number;
  original_filename: string;
  archive_type: 'zip' | '7z' | 'rar';
  selected_types: string[];
  status: 'uploading' | 'processing' | 'done' | 'failed';
  progress: number;
  total_entries: number;
  matched_count: number;
  matched_by_type?: Record<string, number>;
  skipped_count: number;
  failed_reason?: string;
  result_zip_path?: string;
  created_at: string;
  updated_at: string;
  finished_at?: string;
}

export interface CleaningTaskListItem {
  id: number;
  original_filename: string;
  selected_types: string[];
  status: 'uploading' | 'processing' | 'done' | 'failed';
  progress: number;
  matched_count: number;
  created_at: string;
  finished_at?: string;
}

export interface AdminCleaningTaskListItem extends CleaningTaskListItem {
  user_id: number;
  username?: string;
}

class CleaningService {
  async createTask(file: File, selectedTypes: string[]) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('selected_types', JSON.stringify(selectedTypes));
    return apiClient.post<CleaningTask>('/cleaning/tasks', formData);
  }

  async getUserTasks() {
    return apiClient.get<CleaningTaskListItem[]>('/cleaning/tasks');
  }

  async getTaskDetail(taskId: number) {
    return apiClient.get<CleaningTask>(`/cleaning/tasks/${taskId}`);
  }

  async downloadResult(taskId: number) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/cleaning/tasks/${taskId}/download`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('下载失败');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cleaned_${taskId}.zip`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  async retryTask(taskId: number) {
    return apiClient.post<CleaningTask>(`/cleaning/tasks/${taskId}/retry`);
  }

  async deleteTask(taskId: number) {
    return apiClient.delete(`/cleaning/tasks/${taskId}`);
  }

  async batchDeleteUserTasks(taskIds: number[]) {
    return apiClient.delete<{ deleted: number }>(`/cleaning/tasks?${taskIds.map(id => `task_ids=${id}`).join('&')}`);
  }

  async getAllTasks() {
    return apiClient.get<AdminCleaningTaskListItem[]>('/admin/cleaning/tasks');
  }

  async batchDeleteTasks(taskIds: number[]) {
    return apiClient.post('/admin/cleaning/tasks/batch-delete', taskIds);
  }
}

export const cleaningService = new CleaningService();
