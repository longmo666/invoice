import type { AdminPaginatedTaskItem, AdminTaskSummary, TaskStatus, InvoiceType } from '../../../lib/types/recognition';

export type AdminRecognitionTab = 'invoice' | 'train';

export interface AdminTaskRow extends AdminPaginatedTaskItem {
  checked: boolean;
}

export type { AdminPaginatedTaskItem, AdminTaskSummary, TaskStatus, InvoiceType };
