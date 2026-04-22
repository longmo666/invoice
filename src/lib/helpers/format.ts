/**
 * 共享格式化函数
 *
 * 收口所有组件中重复的格式化/映射逻辑
 */

// ==================== 时间格式化 ====================

/**
 * 将后端返回的时间字符串格式化为北京时间显示。
 * 后端数据库存储的是 UTC 时间（无时区标记），
 * 因此解析时需要显式标记为 UTC 再转换。
 */
export function formatBeijingTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    // 如果字符串没有时区标记（没有 Z 或 +/-），追加 Z 表示 UTC
    let normalized = dateStr.trim();
    if (!/[Zz]$/.test(normalized) && !/[+-]\d{2}:\d{2}$/.test(normalized)) {
      normalized += "Z";
    }
    return new Date(normalized).toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" });
  } catch {
    return dateStr;
  }
}

// ==================== 复核状态映射 ====================

const REVIEW_STATUS_MAP: Record<string, string> = {
  auto_passed: "自动通过",
  pending_review: "待人工复核",
  manual_confirmed: "人工已确认",
};

export function mapReviewStatus(status: string): string {
  return REVIEW_STATUS_MAP[status] || status;
}

// ==================== 发票类型映射 ====================

const INVOICE_TYPE_MAP: Record<string, string> = {
  vat_special: "增值税专用发票",
  vat_normal: "增值税普通发票",
  railway_ticket: "铁路客运发票",
};

export function mapInvoiceType(type: string): string {
  return INVOICE_TYPE_MAP[type] || type;
}
