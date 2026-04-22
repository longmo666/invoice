/**
 * 待复核模块字段提取 helper
 * 将 PendingReviewItem 中的字段按发票类型提取为展示用结构
 * 页面只负责加载/分页/提交，不再管字段提取
 */
import type { PendingReviewItem } from "../types/recognition";

// ==================== 通用工具 ====================

/** 判断是否为高铁票类型 */
export function isTrainInvoiceType(invoiceType: string): boolean {
  return invoiceType === "railway_ticket";
}

/** 从 item 提取最佳 result 对象 */
export function getResultData(item: PendingReviewItem): Record<string, any> {
  return item.reviewed_result || item.original_result || {};
}

// ==================== 列表展示 ====================

/** 表格列定义 */
export interface ColumnDef {
  key: string;
  label: string;
  /** result 中的字段名，如果是 item 级字段则为 null */
  resultField?: string;
}

/** 高铁票表格列 */
export const TRAIN_TABLE_COLUMNS: ColumnDef[] = [
  { key: "ticket_id", label: "电子客票号", resultField: "ticket_id" },
  { key: "train_number", label: "车次", resultField: "train_number" },
  { key: "passenger_name", label: "乘客", resultField: "passenger_name" },
  { key: "departure_station", label: "出发站", resultField: "departure_station" },
  { key: "train_date", label: "发车日期", resultField: "train_date" },
  { key: "ticket_price", label: "票价", resultField: "ticket_price" },
];

/** 普通发票表格列 */
export const INVOICE_TABLE_COLUMNS: ColumnDef[] = [
  { key: "invoice_number", label: "发票号码", resultField: "invoice_number" },
  { key: "buyer_name", label: "购买方", resultField: "buyer_name" },
  { key: "seller_name", label: "销售方", resultField: "seller_name" },
  { key: "invoice_date", label: "开票日期", resultField: "invoice_date" },
  { key: "total_amount", label: "价税合计", resultField: "total_amount" },
];

/** 根据 invoiceType 获取表格列定义 */
export function getTableColumns(invoiceType: string): ColumnDef[] {
  return isTrainInvoiceType(invoiceType) ? TRAIN_TABLE_COLUMNS : INVOICE_TABLE_COLUMNS;
}

/** 移动端卡片摘要 */
export interface CardSummary {
  title: string;
  subtitle: string;
  amount: string;
}

/** 从 result 提取移动端卡片摘要 */
export function extractCardSummary(result: Record<string, any>, invoiceType: string): CardSummary {
  if (isTrainInvoiceType(invoiceType)) {
    return {
      title: `${result.train_number || "未知车次"} · ${result.passenger_name || ""}`,
      subtitle: `${result.departure_station || ""} · ${result.train_date || ""}`,
      amount: result.ticket_price || "",
    };
  }
  return {
    title: result.invoice_number || "未知发票号",
    subtitle: result.buyer_name || "",
    amount: result.total_amount || "",
  };
}

/** 移动端卡片的额外行（发票显示销售方+金额，高铁票只显示票价） */
export function extractCardExtra(result: Record<string, any>, invoiceType: string): { seller?: string; amount?: string } | null {
  if (isTrainInvoiceType(invoiceType)) return null;
  return {
    seller: result.seller_name || "",
    amount: result.total_amount || "",
  };
}

// ==================== 编辑字段 ====================

export interface EditFieldDef {
  key: string;
  label: string;
}

/** 高铁票编辑字段定义 */
export const TRAIN_EDIT_FIELDS: readonly EditFieldDef[] = [
  { key: "invoice_type", label: "发票类型" },
  { key: "invoice_number", label: "发票号码" },
  { key: "invoice_date", label: "开票日期" },
  { key: "train_number", label: "车次号" },
  { key: "departure_station", label: "起始站" },
  { key: "train_date", label: "发车日期" },
  { key: "seat_class", label: "座位等级" },
  { key: "ticket_price", label: "票价" },
  { key: "passenger_name", label: "乘车人" },
  { key: "ticket_id", label: "电子客票号" },
  { key: "buyer_name", label: "购买方名称" },
  { key: "buyer_credit_code", label: "购买方信用代码" },
];

/** 普通发票编辑字段定义 */
export const INVOICE_EDIT_FIELDS: readonly EditFieldDef[] = [
  { key: "invoice_type", label: "发票类型" },
  { key: "invoice_number", label: "发票号码" },
  { key: "invoice_date", label: "开票日期" },
  { key: "buyer_name", label: "购买方名称" },
  { key: "buyer_tax_number", label: "购买方税号" },
  { key: "seller_name", label: "销售方名称" },
  { key: "seller_tax_number", label: "销售方税号" },
  { key: "amount", label: "金额" },
  { key: "tax_amount", label: "税额" },
  { key: "total_amount", label: "价税合计" },
];

/** 根据 invoiceType 获取编辑字段列表 */
export function getEditFields(invoiceType: string): readonly EditFieldDef[] {
  return isTrainInvoiceType(invoiceType) ? TRAIN_EDIT_FIELDS : INVOICE_EDIT_FIELDS;
}
