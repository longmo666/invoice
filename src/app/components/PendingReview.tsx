/**
 * 待复核 — 纯壳组件
 * 所有状态与副作用委托给 usePendingReview
 * 本文件只做：Outlet context → hook → 布局
 */
import { useOutletContext } from "react-router";
import {
  RefreshCw,
  AlertCircle,
  ClipboardCheck,
  X,
  CheckCircle2,
  Trash2,
} from "lucide-react";
import HelpTip from "./HelpTip";
import Pagination from "./Pagination";
import { ConfidenceBadge } from "./StatusBadge";
import {
  getResultData,
  getTableColumns,
  extractCardSummary,
  getEditFields,
} from "../../lib/helpers/pendingReview";
import { usePendingReview } from "./pending-review/usePendingReview";

export default function PendingReview() {
  const { activeMenu, isMobile } = useOutletContext<{ activeMenu: string; isMobile: boolean }>();
  const pr = usePendingReview(activeMenu);

  const tabInvoiceType = pr.isTrainTicket ? "railway_ticket" : "vat_normal";
  const tableColumns = getTableColumns(tabInvoiceType);
  const editFields = pr.reviewingItem
    ? getEditFields(pr.reviewingItem.invoice_type || tabInvoiceType)
    : [];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className={`${isMobile ? "px-4 py-4" : "px-6 py-5"} border-b border-border flex items-center gap-3 bg-card/50`}>
        <div className={`${isMobile ? "w-8 h-8" : "w-9 h-9"} rounded-xl bg-amber-50 dark:bg-amber-500/10 flex items-center justify-center`}>
          <ClipboardCheck className={`${isMobile ? "w-4 h-4" : "w-5 h-5"} text-amber-600 dark:text-amber-400`} />
        </div>
        <div className="flex-1 min-w-0">
          <h2 className={`${isMobile ? "text-[15px]" : "text-[17px]"} truncate`}>待复核 · {pr.isTrainTicket ? "高铁票" : "普通发票"}</h2>
          {!isMobile && <p className="text-[12px] text-muted-foreground mt-0.5">需要人工确认的识别结果</p>}
        </div>
        <span className="text-[12px] text-muted-foreground bg-muted px-2.5 py-1 rounded-full shrink-0">{pr.items.length} 条</span>
        {!isMobile && <HelpTip text="待复核列表展示 AI 识别后置信度较低或存在疑问的记录，需人工确认后方可入库。" />}
        <button onClick={pr.loadPendingItems} disabled={pr.refreshing}
          className={`flex items-center gap-1.5 ${isMobile ? "px-3 py-1.5 text-[13px]" : "px-4 py-2 text-[14px]"} border border-border rounded-xl hover:bg-accent transition-all duration-200 disabled:opacity-50 shrink-0`}>
          <RefreshCw className={`w-4 h-4 ${pr.refreshing ? "animate-spin" : ""}`} />
          {isMobile ? "" : pr.refreshing ? "刷新中..." : "刷新"}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {isMobile ? (
          <div className="p-4 space-y-3">
            {pr.paged.length === 0 && (
              <div className="text-center py-16 text-[14px] text-muted-foreground">暂无待复核记录</div>
            )}
            {pr.paged.map((item) => {
              const result = getResultData(item);
              const card = extractCardSummary(result, item.invoice_type || tabInvoiceType);
              return (
                <div key={item.id} className="bg-card rounded-xl border border-border p-4 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="text-[14px] font-medium truncate">{card.title}</p>
                      <p className="text-[12px] text-muted-foreground mt-0.5 truncate">{card.subtitle}</p>
                    </div>
                    <ConfidenceBadge score={item.confidence_score} />
                  </div>
                  {card.amount && (
                    <div className="text-[12px] text-primary font-medium">{card.amount}</div>
                  )}
                  <div className="flex items-center gap-1.5 text-[12px] text-amber-600 dark:text-amber-400">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span className="truncate">{item.review_reason || "待人工确认"}</span>
                  </div>
                  <div className="flex items-center gap-2 pt-1">
                    <button onClick={() => pr.handleReview(item)}
                      className="flex-1 text-[13px] py-2 bg-primary text-primary-foreground rounded-lg hover:shadow-md transition-all">
                      复核
                    </button>
                    <button onClick={() => pr.handleVoid(item.id)}
                      className="px-3 py-2 hover:bg-destructive/10 rounded-lg transition-all" title="作废">
                      <Trash2 className="w-4 h-4 text-muted-foreground hover:text-destructive" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/40">
                {tableColumns.map((col) => (
                  <th key={col.key} className="text-left px-5 py-3.5 text-[13px] text-muted-foreground whitespace-nowrap">{col.label}</th>
                ))}
                <th className="text-left px-5 py-3.5 text-[13px] text-muted-foreground whitespace-nowrap">置信度</th>
                <th className="text-left px-5 py-3.5 text-[13px] text-muted-foreground whitespace-nowrap">待复核原因</th>
                <th className="text-left px-5 py-3.5 text-[13px] text-muted-foreground whitespace-nowrap">操作</th>
              </tr>
            </thead>
            <tbody>
              {pr.paged.map((item) => {
                const result = getResultData(item);
                return (
                  <tr key={item.id} className="border-b border-border hover:bg-accent/40 transition-colors duration-150">
                    {tableColumns.map((col) => (
                      <td key={col.key} className="px-5 py-4 text-[13px] max-w-[180px] truncate">
                        {col.resultField ? (result[col.resultField] || "") : ""}
                      </td>
                    ))}
                    <td className="px-5 py-4 text-[13px]">
                      <ConfidenceBadge score={item.confidence_score} />
                    </td>
                    <td className="px-5 py-4">
                      <span className="flex items-center gap-1.5 text-[12px] text-amber-600 dark:text-amber-400">
                        <AlertCircle className="w-3.5 h-3.5" /> {item.review_reason || "待人工确认"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1.5">
                        <button onClick={() => pr.handleReview(item)}
                          className="text-[13px] px-4 py-1.5 bg-primary text-primary-foreground rounded-lg hover:shadow-md hover:shadow-primary/20 transition-all duration-200">
                          复核
                        </button>
                        <button onClick={() => pr.handleVoid(item.id)}
                          className="p-1.5 hover:bg-destructive/10 rounded-lg" title="作废">
                          <Trash2 className="w-4 h-4 text-muted-foreground hover:text-destructive" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <Pagination
        page={pr.page} totalPages={pr.totalPages} pageSize={pr.pageSize} total={pr.items.length}
        onPageChange={pr.setPage}
        onPageSizeChange={(s) => { pr.setPageSize(s); pr.setPage(1); }}
      />

      {/* Review Modal */}
      {pr.reviewingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => pr.setReviewingId(null)}>
          <div className={`bg-card rounded-2xl border border-border shadow-2xl ${isMobile ? "mx-4 w-full max-h-[90vh]" : "w-[600px] max-h-[80vh]"} overflow-auto`} onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-5 border-b border-border flex items-center justify-between sticky top-0 bg-card z-10">
              <h3 className="text-[17px]">复核 · {pr.isTrainTicket ? "高铁票" : "普通发票"}</h3>
              <button onClick={() => pr.setReviewingId(null)} className="p-1.5 hover:bg-accent rounded-lg transition-all"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-[14px]">待复核原因</p>
                  <p className="text-[13px] text-muted-foreground mt-0.5">{pr.reviewingItem.review_reason || "待人工确认"}</p>
                </div>
              </div>
              {editFields.map((field) => (
                <EditField
                  key={field.key}
                  label={field.label}
                  value={pr.editedData[field.key] || ""}
                  onChange={(v) => pr.handleFieldChange(field.key, v)}
                />
              ))}
            </div>
            <div className="px-6 py-5 border-t border-border flex gap-3 justify-end sticky bottom-0 bg-card">
              <button onClick={() => pr.setReviewingId(null)}
                className="px-5 py-2.5 text-[14px] border border-border rounded-xl hover:bg-accent transition-all">取消</button>
              <button onClick={pr.handleConfirm} disabled={pr.submitting}
                className="flex items-center gap-2 px-5 py-2.5 text-[14px] bg-primary text-primary-foreground rounded-xl hover:shadow-lg hover:shadow-primary/20 transition-all disabled:opacity-50">
                {pr.submitting ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                确认通过
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EditField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="block text-[13px] text-muted-foreground mb-1">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 rounded-lg border border-border bg-background text-[14px] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all"
      />
    </div>
  );
}
