/**
 * 识别任务相关类型定义与常量
 */

export type InvoiceType = 'vat_special' | 'vat_normal' | 'railway_ticket';
export type RecognitionMode = 'local_ocr' | 'ai' | 'hybrid';
export type TaskStatus = 'uploading' | 'processing' | 'done' | 'failed';
export type ReviewStatus = 'auto_passed' | 'pending_review' | 'manual_confirmed';

// 状态显示文案映射
export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  uploading: '上传中',
  processing: '处理中',
  done: '已完成',
  failed: '失败',
};

// 状态颜色映射
export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
  uploading: 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400',
  processing: 'bg-yellow-50 dark:bg-yellow-500/10 text-yellow-600 dark:text-yellow-400',
  done: 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  failed: 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400',
};

export interface RecognitionTask {
  id: number;
  original_filename: string;
  file_type: string;
  invoice_type: InvoiceType;
  recognition_mode: RecognitionMode;
  status: TaskStatus;
  progress: number | null;
  total_items: number | null;
  success_items: number | null;
  failed_items: number | null;
  error_message: string | null;
  created_at: string;
  finished_at: string | null;
}

export interface RecognitionItem {
  id: number;
  task_id: number;
  page_number: number | null;
  item_index: number;
  original_result: any;
  reviewed_result: any;
  review_status: ReviewStatus;
  review_reason: string | null;
  confidence_score: number | null;
  created_at: string;
}

export interface RecognitionTaskDetail extends RecognitionTask {
  items: RecognitionItem[];
}

export interface CreateTaskResponse {
  id: number;
  status: TaskStatus;
  progress: number;
  created_at: string;
}

/** 分页任务摘要（服务端已聚合，无需逐条查详情） */
export interface PaginatedTaskItem {
  id: number;
  original_filename: string;
  file_type: string | null;
  invoice_type: InvoiceType | null;
  status: TaskStatus | null;
  progress: number | null;
  total_items: number | null;
  success_items: number | null;
  failed_items: number | null;
  error_message: string | null;
  created_at: string | null;
  finished_at: string | null;
  confidence_score: number | null;
  review_status: ReviewStatus | null;
  summary: Record<string, any>;
}

export interface PaginatedTasksResponse {
  items: PaginatedTaskItem[];
  total: number;
  page: number;
  page_size: number;
}

// ==================== 管理端分页摘要 ====================

export interface AdminTaskSummary {
  invoice_number: string;
  invoice_date: string;
  buyer_name: string;
  seller_name: string;
  total_amount: string;
  train_number: string;
  departure_station: string;
  train_date: string;
  ticket_price: string;
  passenger_name: string;
  ticket_id: string;
  seat_class: string;
  deductible_tax: string;
}

export interface AdminPaginatedTaskItem {
  id: number;
  user_id: number;
  username: string;
  original_filename: string;
  invoice_type: InvoiceType | null;
  status: TaskStatus | null;
  created_at: string | null;
  confidence_score: number | null;
  error_message: string | null;
  summary: AdminTaskSummary;
}

export interface AdminPaginatedTasksResponse {
  items: AdminPaginatedTaskItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ==================== AI 诊断步骤 ====================

export interface DiagnosticStep {
  step: string;
  url: string;
  status_code: number | null;
  latency_ms: number | null;
  success: boolean;
  detail: string;
}

// ==================== 待复核项（含 task 级字段） ====================

export interface PendingReviewItem extends RecognitionItem {
  task_filename: string;
  invoice_type: string;
}
