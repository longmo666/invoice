import { apiClient } from '../api/client';
import type {
  InvoiceType,
  RecognitionMode,
  TaskStatus,
  RecognitionTask,
  RecognitionTaskDetail,
  RecognitionItem,
  CreateTaskResponse,
  PaginatedTasksResponse,
  AdminPaginatedTasksResponse,
  PendingReviewItem,
} from '../types/recognition';

// 重新导出类型和常量，保持现有 import 路径不变
export type { InvoiceType, RecognitionMode, TaskStatus, ReviewStatus, RecognitionTask, RecognitionTaskDetail, RecognitionItem, CreateTaskResponse, PaginatedTaskItem, PaginatedTasksResponse, AdminPaginatedTaskItem, AdminPaginatedTasksResponse, PendingReviewItem, DiagnosticStep } from '../types/recognition';
export { TASK_STATUS_LABELS, TASK_STATUS_COLORS } from '../types/recognition';

export const recognitionService = {
  // 创建识别任务
  async createTask(
    file: File,
    invoiceType: InvoiceType,
    recognitionMode: RecognitionMode = 'ai'
  ) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('invoice_type', invoiceType);
    formData.append('recognition_mode', recognitionMode);

    return apiClient.post<CreateTaskResponse>('/recognition/tasks', formData);
  },

  // 获取任务列表
  async getTasks(invoiceType?: InvoiceType, status?: TaskStatus) {
    let endpoint = '/recognition/tasks?';
    if (invoiceType) endpoint += `invoice_type=${invoiceType}&`;
    if (status) endpoint += `status=${status}&`;
    return apiClient.get<RecognitionTask[]>(endpoint);
  },

  // 获取任务详情
  async getTaskDetail(taskId: number) {
    return apiClient.get<RecognitionTaskDetail>(`/recognition/tasks/${taskId}`);
  },

  // 获取待复核项
  async getPendingReviewItems(invoiceType?: InvoiceType) {
    const qs = invoiceType ? `?invoice_type=${invoiceType}` : '';
    return apiClient.get<PendingReviewItem[]>(`/recognition/pending-review${qs}`);
  },

  // 更新复核结果
  async updateReview(itemId: number, reviewedResult: any) {
    return apiClient.put(`/recognition/items/${itemId}/review`, {
      reviewed_result: reviewedResult,
      review_status: "manual_confirmed",
    });
  },

  // 作废复核项（物理删除）
  async voidReviewItem(itemId: number) {
    return apiClient.delete(`/recognition/items/${itemId}`);
  },

  // 导出为 CSV
  async exportToCsv(taskId: number) {
    await apiClient.downloadFile(
      `/recognition/tasks/${taskId}/export/csv`,
      `invoice_${taskId}_${Date.now()}.csv`
    );
  },

  // 导出为 Excel
  async exportToExcel(taskId: number) {
    await apiClient.downloadFile(
      `/recognition/tasks/${taskId}/export/excel`,
      `invoice_${taskId}_${Date.now()}.xlsx`
    );
  },

  // 删除任务（物理删除）
  async deleteTask(taskId: number) {
    return apiClient.delete(`/recognition/tasks/${taskId}`);
  },

  // 获取文件预览 URL（带 token 认证，供 img/iframe 使用）
  getPreviewUrl(taskId: number): string {
    const token = localStorage.getItem('access_token') || '';
    return apiClient.getFullUrl(`/recognition/tasks/${taskId}/preview?token=${encodeURIComponent(token)}`);
  },

  // 获取任务列表（分页，服务端聚合摘要）
  async getTasksPaginated(params: {
    invoiceType?: InvoiceType;
    status?: TaskStatus;
    keyword?: string;
    page?: number;
    pageSize?: number;
  }) {
    const qs = new URLSearchParams();
    if (params.invoiceType) qs.set('invoice_type', params.invoiceType);
    if (params.status) qs.set('status', params.status);
    if (params.keyword) qs.set('keyword', params.keyword);
    if (params.page) qs.set('page', String(params.page));
    if (params.pageSize) qs.set('page_size', String(params.pageSize));
    return apiClient.get<PaginatedTasksResponse>(`/recognition/tasks/paginated?${qs.toString()}`);
  },

  // 批量删除任务
  async batchDeleteTasks(taskIds: number[]) {
    return apiClient.post<{ deleted: number }>('/recognition/tasks/batch-delete', { task_ids: taskIds });
  },

    // ==================== 管理员接口 ====================

  // 管理员获取任务详情
  async adminGetTaskDetail(taskId: number) {
    return apiClient.get<RecognitionTaskDetail>(`/recognition/admin/tasks/${taskId}`);
  },

  // 管理员批量删除
  async adminDeleteTasks(taskIds: number[]) {
    return apiClient.delete<{ deleted: number }>(`/recognition/admin/tasks?${taskIds.map(id => `task_ids=${id}`).join('&')}`);
  },

  // 管理员导出 CSV
  async adminExportToCsv(taskId: number) {
    await apiClient.downloadFile(
      `/recognition/admin/tasks/${taskId}/export/csv`,
      `invoice_${taskId}_${Date.now()}.csv`
    );
  },

  // 管理员导出 Excel
  async adminExportToExcel(taskId: number) {
    await apiClient.downloadFile(
      `/recognition/admin/tasks/${taskId}/export/excel`,
      `invoice_${taskId}_${Date.now()}.xlsx`
    );
  },

  // 管理员分页获取任务列表（含摘要，消除 N+1）
  async adminGetTasksPaginated(params: {
    tab: 'invoice' | 'train';
    invoiceType?: InvoiceType;
    status?: TaskStatus;
    keyword?: string;
    page?: number;
    pageSize?: number;
  }) {
    const qs = new URLSearchParams();
    qs.set('tab', params.tab);
    if (params.invoiceType) qs.set('invoice_type', params.invoiceType);
    if (params.status) qs.set('status', params.status);
    if (params.keyword) qs.set('keyword', params.keyword);
    if (params.page) qs.set('page', String(params.page));
    if (params.pageSize) qs.set('page_size', String(params.pageSize));
    return apiClient.get<AdminPaginatedTasksResponse>(`/recognition/admin/tasks/paginated?${qs.toString()}`);
  },
};
