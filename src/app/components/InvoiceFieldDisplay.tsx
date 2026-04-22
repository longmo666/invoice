/**
 * 共享的发票字段展示组件
 * 用于统一 RecordList、AdminInvoices 等页面的详情弹窗展示
 */

import type { DetailedInvoiceFields } from "../../lib/helpers/recognitionResult";
import { calculateDeductibleTax, formatDeductibleTax } from "../../lib/helpers/deductibleTax";
import { mapReviewStatus } from "../../lib/helpers/format";

interface FieldProps {
  label: string;
  value: string | undefined;
  mono?: boolean;
}

function Field({ label, value, mono = false }: FieldProps) {
  const displayValue = value || "-";
  return (
    <div className="grid grid-cols-[120px_1fr] gap-3 text-[13px]">
      <span className="text-muted-foreground">{label}</span>
      <span className={`${mono ? "font-mono" : ""} ${!value ? "text-muted-foreground/50" : ""}`}>{displayValue}</span>
    </div>
  );
}

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <div className="space-y-2">
      <h5 className="text-[13px] font-medium text-foreground/80 border-b border-border/50 pb-1">
        {title}
      </h5>
      <div className="space-y-2 pl-2">{children}</div>
    </div>
  );
}

interface InvoiceFieldDisplayProps {
  fields: DetailedInvoiceFields | null;
  invoiceType?: string; // 可选，明确指定类型
}

export default function InvoiceFieldDisplay({ fields, invoiceType }: InvoiceFieldDisplayProps) {
  if (!fields) {
    return (
      <div className="text-center py-8 text-[13px] text-muted-foreground">
        暂无识别结果
      </div>
    );
  }

  // 判断是否为高铁票：明确传入类型 或 根据字段特征判断
  const isRailway = invoiceType === "railway_ticket"
    || !!(fields.train_number || fields.ticket_id || fields.departure_station || fields.passenger_name);

  // 计算可抵扣税额
  const deductibleType = isRailway ? "railway_ticket" : (invoiceType || "vat_normal");
  const deductibleResult: Record<string, any> = {};
  if (fields.invoice_type) deductibleResult.invoice_type = fields.invoice_type;
  if (fields.ticket_price) deductibleResult.ticket_price = fields.ticket_price;
  if (fields.tax_amount) deductibleResult.tax_amount = fields.tax_amount;
  if (fields.amount_excluding_tax) deductibleResult.amount_excluding_tax = fields.amount_excluding_tax;
  if (fields.tax_rate) deductibleResult.tax_rate = fields.tax_rate;
  if (fields.total_amount) deductibleResult.total_amount = fields.total_amount;
  const deductible = calculateDeductibleTax(deductibleResult, deductibleType);
  const deductibleStr = formatDeductibleTax(deductible);

  if (isRailway) {
    return (
      <div className="space-y-3">
        <Section title="票据信息">
          <Field label="发票类型" value={fields.invoice_type} />
          <Field label="发票号码" value={fields.invoice_number} mono />
          <Field label="开票日期" value={fields.invoice_date} />
        </Section>

        <Section title="行程信息">
          <Field label="车次号" value={fields.train_number} />
          <Field label="起始站" value={fields.departure_station} />
          <Field label="发车日期" value={fields.train_date} />
          <Field label="座位等级" value={fields.seat_class} />
          <Field label="票价" value={fields.ticket_price} />
          <Field label="可抵扣税额" value={deductibleStr !== '-' ? deductibleStr : "不可抵扣"} />
        </Section>

        <Section title="乘车人信息">
          <Field label="乘车人" value={fields.passenger_name} />
          <Field label="电子客票号" value={fields.ticket_id} mono />
        </Section>

        <Section title="购买方">
          <Field label="购买方名称" value={fields.buyer_name} />
          <Field label="统一社会信用代码" value={fields.buyer_credit_code || fields.buyer_tax_id} mono />
        </Section>

        <div className="pt-2 border-t border-border/50 flex items-center gap-4">
          {fields.confidence_score !== undefined && fields.confidence_score !== null && (
            <div className="text-[13px] text-muted-foreground">
              置信度: <span className="text-foreground font-medium">{(fields.confidence_score * 100).toFixed(1)}%</span>
            </div>
          )}
          {fields.review_status && (
            <div className="text-[13px] text-muted-foreground">
              复核状态: <span className="text-foreground font-medium">{mapReviewStatus(fields.review_status)}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <Section title="发票信息">
        <Field label="发票类型" value={fields.invoice_type} />
        <Field label="发票号码" value={fields.invoice_number} mono />
        <Field label="开票日期" value={fields.invoice_date} />
      </Section>

      <Section title="购买方">
        <Field label="购买方名称" value={fields.buyer_name} />
        <Field label="购买方税号" value={fields.buyer_tax_id} mono />
        <Field label="地址电话" value={fields.buyer_address_phone} />
        <Field label="开户行账号" value={fields.buyer_bank_account} />
      </Section>

      <Section title="销售方">
        <Field label="销售方名称" value={fields.seller_name} />
        <Field label="销售方税号" value={fields.seller_tax_id} mono />
        <Field label="地址电话" value={fields.seller_address_phone} />
        <Field label="开户行账号" value={fields.seller_bank_account} />
      </Section>

      <Section title="项目与金额">
        <Field label="项目名称" value={fields.item_name} />
        <Field label="不含税金额" value={fields.amount_excluding_tax} />
        <Field label="税率" value={fields.tax_rate} />
        <Field label="税额" value={fields.tax_amount} />
      </Section>

      <Section title="价税合计">
        <Field label="价税合计大写" value={fields.total_amount_cn} />
        <Field label="价税合计小写" value={fields.total_amount} />
        <Field label="可抵扣税额" value={deductibleStr !== '-' ? deductibleStr : "不可抵扣"} />
      </Section>

      <Section title="其他">
        <Field label="收款人" value={fields.payee} />
        <Field label="复核人" value={fields.reviewer} />
        <Field label="开票人" value={fields.issuer} />
      </Section>

      <div className="pt-2 border-t border-border/50 flex items-center gap-4">
        {fields.confidence_score !== undefined && fields.confidence_score !== null && (
          <div className="text-[13px] text-muted-foreground">
            置信度: <span className="text-foreground font-medium">{(fields.confidence_score * 100).toFixed(1)}%</span>
          </div>
        )}
        {fields.review_status && (
          <div className="text-[13px] text-muted-foreground">
            复核状态: <span className="text-foreground font-medium">{mapReviewStatus(fields.review_status)}</span>
          </div>
        )}
      </div>
    </div>
  );
}
