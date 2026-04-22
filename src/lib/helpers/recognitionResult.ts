/**
 * 识别结果处理 helper
 * 提供任务恢复、结果提取、字段映射等共享逻辑
 */

import type { RecognitionTaskDetail, RecognitionItem } from '../services/recognition';

/**
 * 从任务详情提取主结果（用于列表摘要）
 */
export interface InvoiceSummary {
  invoice_number?: string;
  invoice_date?: string;
  buyer_name?: string;
  buyer_tax_id?: string;
  seller_name?: string;
  seller_tax_id?: string;
  item_name?: string;
  tax_rate?: string;
  tax_amount?: string;
  total_amount?: string;
  issuer?: string;
  confidence_score?: number;
  review_status?: string;
}

export function extractMainResult(task: RecognitionTaskDetail): InvoiceSummary | null {
  if (!task.items || task.items.length === 0) {
    return null;
  }

  // 使用最佳结果项
  const bestItem = getBestResultItem(task.items);
  if (!bestItem) return null;

  const result = bestItem.reviewed_result || bestItem.original_result || {};

  return {
    invoice_number: result.invoice_number || '',
    invoice_date: result.invoice_date || '',
    buyer_name: result.buyer_name || '',
    buyer_tax_id: result.buyer_tax_id || '',
    seller_name: result.seller_name || '',
    seller_tax_id: result.seller_tax_id || '',
    item_name: result.item_name || '',
    tax_rate: result.tax_rate || '',
    tax_amount: result.tax_amount || '',
    total_amount: result.total_amount || '',
    issuer: result.issuer || '',
    confidence_score: bestItem.confidence_score,
    review_status: bestItem.review_status,
  };
}

/**
 * 获取任务的最佳结果项（最高置信度或已复核）
 */
export function getBestResultItem(items: RecognitionItem[]): RecognitionItem | null {
  if (!items || items.length === 0) {
    return null;
  }

  // 优先返回已人工确认的
  const confirmed = items.find(item => item.review_status === 'manual_confirmed');
  if (confirmed) return confirmed;

  // 其次返回自动通过的
  const autoPassed = items.find(item => item.review_status === 'auto_passed');
  if (autoPassed) return autoPassed;

  // 最后按置信度排序
  const sorted = [...items].sort((a, b) => {
    const scoreA = a.confidence_score || 0;
    const scoreB = b.confidence_score || 0;
    return scoreB - scoreA;
  });

  return sorted[0];
}

/**
 * 从最佳结果项中提取完整字段（用于详情展示）
 */
export interface DetailedInvoiceFields {
  // 发票信息
  invoice_type?: string;
  invoice_number?: string;
  invoice_date?: string;

  // 购买方
  buyer_name?: string;
  buyer_tax_id?: string;
  buyer_address_phone?: string;
  buyer_bank_account?: string;

  // 销售方
  seller_name?: string;
  seller_tax_id?: string;
  seller_address_phone?: string;
  seller_bank_account?: string;

  // 项目与金额
  item_name?: string;
  amount_excluding_tax?: string;
  tax_rate?: string;
  tax_amount?: string;

  // 价税合计
  total_amount_cn?: string;
  total_amount?: string;

  // 其他
  issuer?: string;
  payee?: string;
  reviewer?: string;

  // 高铁票字段
  train_number?: string;
  departure_station?: string;
  train_date?: string;
  seat_class?: string;
  ticket_price?: string;
  passenger_name?: string;
  ticket_id?: string;
  buyer_credit_code?: string;

  // 元数据
  confidence_score?: number;
  review_status?: string;
}

export function extractDetailedFields(item: RecognitionItem | null): DetailedInvoiceFields | null {
  if (!item) return null;

  const result = item.reviewed_result || item.original_result || {};

  return {
    // 发票信息
    invoice_type: result.invoice_type || '',
    invoice_number: result.invoice_number || '',
    invoice_date: result.invoice_date || '',

    // 购买方
    buyer_name: result.buyer_name || '',
    buyer_tax_id: result.buyer_tax_id || '',
    buyer_address_phone: result.buyer_address_phone || '',
    buyer_bank_account: result.buyer_bank_account || '',

    // 销售方
    seller_name: result.seller_name || '',
    seller_tax_id: result.seller_tax_id || '',
    seller_address_phone: result.seller_address_phone || '',
    seller_bank_account: result.seller_bank_account || '',

    // 项目与金额
    item_name: result.item_name || '',
    amount_excluding_tax: result.amount_excluding_tax || '',
    tax_rate: result.tax_rate || '',
    tax_amount: result.tax_amount || '',

    // 价税合计
    total_amount_cn: result.total_amount_cn || '',
    total_amount: result.total_amount || '',

    // 其他
    issuer: result.issuer || '',
    payee: result.payee || '',
    reviewer: result.reviewer || '',

    // 高铁票字段
    train_number: result.train_number || '',
    departure_station: result.departure_station || '',
    train_date: result.train_date || '',
    seat_class: result.seat_class || '',
    ticket_price: result.ticket_price || '',
    passenger_name: result.passenger_name || '',
    ticket_id: result.ticket_id || '',
    buyer_credit_code: result.buyer_credit_code || '',

    // 元数据
    confidence_score: item.confidence_score,
    review_status: item.review_status,
  };
}

/**
 * 标准化结果字段（兼容 snake_case 和 camelCase）
 */
export function normalizeResult(result: any): any {
  if (!result) return {};

  return {
    // 发票信息
    invoice_type: result.invoice_type || '',
    invoice_code: result.invoice_code || '',
    invoice_number: result.invoice_number || '',
    invoice_date: result.invoice_date || '',

    // 购买方
    buyer_name: result.buyer_name || '',
    buyer_tax_id: result.buyer_tax_id || '',
    buyer_address_phone: result.buyer_address_phone || '',
    buyer_bank_account: result.buyer_bank_account || '',

    // 销售方
    seller_name: result.seller_name || '',
    seller_tax_id: result.seller_tax_id || '',
    seller_address_phone: result.seller_address_phone || '',
    seller_bank_account: result.seller_bank_account || '',

    // 项目与金额
    item_name: result.item_name || '',
    amount_excluding_tax: result.amount_excluding_tax || '',
    tax_rate: result.tax_rate || '',
    tax_amount: result.tax_amount || '',

    // 价税合计
    total_amount_cn: result.total_amount_cn || '',
    total_amount: result.total_amount || '',

    // 其他
    payee: result.payee || '',
    reviewer: result.reviewer || '',
    issuer: result.issuer || '',

    // 保留原始数据
    ...result,
  };
}

/**
 * 列表行展示数据（从分页摘要提取）
 *
 * 将 summary 字段提取、状态映射、可抵扣税额计算等逻辑
 * 从 RecordList 组件下沉到此 helper，实现单一职责。
 */
import { calculateDeductibleTax, formatDeductibleTax } from './deductibleTax';
import { formatBeijingTime } from './format';
import { TASK_STATUS_LABELS, type TaskStatus } from '../services/recognition';

export interface ListDisplayData {
  filename: string;
  status: string;
  created_at: string;
  confidence_score: number | null;
  deductible_tax: string;
  // 发票字段
  invoice_number: string;
  invoice_date: string;
  buyer_name: string;
  seller_name: string;
  total_amount: string;
  // 高铁票字段
  train_number: string;
  departure_station: string;
  train_date: string;
  ticket_price: string;
  passenger_name: string;
  ticket_id: string;
  seat_class: string;
}

export function buildListDisplayData(
  summary: Record<string, any>,
  originalFilename: string,
  status: string,
  invoiceType: string,
  createdAt: string,
  confidenceScore: number | null
): ListDisplayData {
  const deductible = calculateDeductibleTax(summary, invoiceType);
  return {
    filename: originalFilename,
    status: TASK_STATUS_LABELS[status as TaskStatus] || status,
    created_at: formatBeijingTime(createdAt),
    confidence_score: confidenceScore,
    deductible_tax: formatDeductibleTax(deductible),
    invoice_number: summary.invoice_number || "-",
    invoice_date: summary.invoice_date || "-",
    buyer_name: summary.buyer_name || "-",
    seller_name: summary.seller_name || "-",
    total_amount: summary.total_amount || "-",
    train_number: summary.train_number || "-",
    departure_station: summary.departure_station || "-",
    train_date: summary.train_date || "-",
    ticket_price: summary.ticket_price || "-",
    passenger_name: summary.passenger_name || "-",
    ticket_id: summary.ticket_id || "-",
    seat_class: summary.seat_class || "-",
  };
}
