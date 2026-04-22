/**
 * 可抵扣税额计算
 *
 * 规则：
 * 1. 增值税专用发票：税额全额可抵扣
 * 2. 增值税普通发票：不可抵扣
 * 3. 铁路客运发票：票价 ÷ (1 + 9%) × 9%
 *
 * 注意：判断专票/普票优先使用识别结果中的 invoice_type 字段
 */

function parseAmount(value: any): number {
  if (value == null || value === '') return 0;
  const cleaned = String(value).replace(/[¥￥$€,，\s]/g, '');
  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : num;
}

function parseTaxRate(value: any): number {
  if (value == null) return 0;
  const s = String(value).trim();
  if (['***', '免税', '不征税', '0', ''].includes(s)) return 0;
  const cleaned = s.replace('%', '').replace('％', '');
  const rate = parseFloat(cleaned);
  if (isNaN(rate)) return 0;
  return rate > 1 ? rate / 100 : rate;
}

/** 根据识别结果判断实际发票类型 */
function detectActualType(result: Record<string, any>, invoiceType: string): 'special' | 'normal' {
  const recognized = String(result.invoice_type || '').trim();
  if (recognized.includes('专用')) return 'special';
  if (recognized.includes('普通')) return 'normal';
  // 回退到任务级别类型
  if (invoiceType === 'vat_special') return 'special';
  return 'normal';
}

export function calculateDeductibleTax(result: Record<string, any>, invoiceType: string): number {
  if (invoiceType === 'railway_ticket') {
    return calcRailwayTicket(result);
  }
  const actualType = detectActualType(result, invoiceType);
  if (actualType === 'special') {
    return calcVatSpecial(result);
  }
  return 0;
}

/** 专票：税额全额抵扣 */
function calcVatSpecial(result: Record<string, any>): number {
  const taxAmount = parseAmount(result.tax_amount);
  if (taxAmount > 0) return Math.round(taxAmount * 100) / 100;

  const amount = parseAmount(result.amount_excluding_tax);
  const rate = parseTaxRate(result.tax_rate);
  if (amount > 0 && rate > 0) return Math.round(amount * rate * 100) / 100;

  const total = parseAmount(result.total_amount);
  if (total > 0 && rate > 0) return Math.round((total / (1 + rate) * rate) * 100) / 100;

  return 0;
}

/** 铁路客运：票价 ÷ 1.09 × 9% */
function calcRailwayTicket(result: Record<string, any>): number {
  const price = parseAmount(result.ticket_price);
  if (price <= 0) return 0;
  return Math.round((price / 1.09 * 0.09) * 100) / 100;
}

export function formatDeductibleTax(amount: number): string {
  if (amount <= 0) return '-';
  return amount.toFixed(2);
}
