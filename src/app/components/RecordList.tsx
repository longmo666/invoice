import { useState, useEffect, useCallback } from "react";
import { useOutletContext } from "react-router";
import {
  Search,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Download,
  Trash2,
  Eye,
  X,
  List,
  SlidersHorizontal,
  RefreshCw,
} from "lucide-react";
import { useAuth } from "./AuthContext";
import {
  recognitionService,
  type RecognitionTaskDetail,
  type InvoiceType,
  type TaskStatus,
  type PaginatedTaskItem,
  TASK_STATUS_LABELS,
} from "../../lib/services/recognition";
import { extractDetailedFields, buildListDisplayData } from "../../lib/helpers/recognitionResult";
import { formatBeijingTime } from "../../lib/helpers/format";
import { TaskStatusBadge, ConfidenceBadge, ReviewStatusBadge } from "./StatusBadge";
import InvoiceFieldDisplay from "./InvoiceFieldDisplay";
import Pagination from "./Pagination";

interface RecordItem extends PaginatedTaskItem {
  checked: boolean;
}

const DEFAULT_PAGE_SIZE = 10;

export default function RecordList() {
  const { activeMenu, isMobile } = useOutletContext<{ activeMenu: string; isMobile: boolean }>();
  const { user } = useAuth();
  const isTrainTicket = activeMenu === "train";

  const [records, setRecords] = useState<RecordItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [modal, setModal] = useState<{ record: RecordItem; detail: RecognitionTaskDetail | null } | null>(null);

  const [filterKeyword, setFilterKeyword] = useState("");
  const [filterProcess, setFilterProcess] = useState("");

  const invoiceType: InvoiceType = isTrainTicket ? "railway_ticket" : "vat_normal";

  const loadRecords = useCallback(async (p?: number) => {
    setLoading(true);
    try {
      const currentPage = p ?? page;
      const statusMap: Record<string, TaskStatus> = { "已完成": "done", "失败": "failed" };
      const response = await recognitionService.getTasksPaginated({
        invoiceType,
        status: statusMap[filterProcess] || undefined,
        keyword: filterKeyword || undefined,
        page: currentPage,
        pageSize,
      });
      if (response.success && response.data) {
        setRecords(response.data.items.map((item) => ({ ...item, checked: false })));
        setTotal(response.data.total);
      }
    } catch (error) {
      console.error("Load records error:", error);
    } finally {
      setLoading(false);
    }
  }, [invoiceType, filterKeyword, filterProcess, page, pageSize]);

  useEffect(() => {
    loadRecords();
  }, [page, pageSize, invoiceType]);

  const handleSearch = () => {
    setPage(1);
    loadRecords(1);
  };

  const totalPages = Math.ceil(total / pageSize) || 1;
  const checkedIds = records.filter((r) => r.checked).map((r) => r.id);
  const checkedCount = checkedIds.length;
  const headerChecked = records.length > 0 && records.every((r) => r.checked);

  const toggleAll = () => {
    const target = !headerChecked;
    setRecords((prev) => prev.map((r) => ({ ...r, checked: target })));
  };

  const resetFilters = async () => {
    setFilterKeyword("");
    setFilterProcess("");
    setPage(1);
    // 直接用空参数请求，不依赖 state 更新
    setLoading(true);
    try {
      const response = await recognitionService.getTasksPaginated({
        invoiceType,
        page: 1,
        pageSize,
      });
      if (response.success && response.data) {
        setRecords(response.data.items.map((item) => ({ ...item, checked: false })));
        setTotal(response.data.total);
      }
    } catch (error) {
      console.error("Load records error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("确定要物理删除该任务？此操作不可恢复。")) return;
    try {
      const resp = await recognitionService.batchDeleteTasks([id]);
      if (resp.success) {
        loadRecords();
      } else {
        alert("删除失败");
      }
    } catch (error) {
      console.error("Delete error:", error);
      alert("删除失败");
    }
  };

  const handleBatchDelete = async () => {
    if (checkedCount === 0) return;
    if (!confirm(`确定要物理删除选中的 ${checkedCount} 条任务？此操作不可恢复。`)) return;
    try {
      const resp = await recognitionService.batchDeleteTasks(checkedIds);
      if (resp.success) {
        loadRecords();
      } else {
        alert("批量删除失败");
      }
    } catch (error) {
      console.error("Batch delete error:", error);
      alert("批量删除失败");
    }
  };

  const handleViewDetail = async (record: RecordItem) => {
    try {
      const response = await recognitionService.getTaskDetail(record.id);
      if (response.success && response.data) {
        setModal({ record, detail: response.data });
      }
    } catch (error) {
      console.error("Load task detail error:", error);
    }
  };

  const handleExportCSV = async () => {
    if (checkedCount === 0) { alert("请先勾选要导出的记录"); return; }
    try {
      for (const id of checkedIds) await recognitionService.exportToCsv(id);
    } catch { alert("导出失败，请重试"); }
  };

  const handleExportExcel = async () => {
    if (checkedCount === 0) { alert("请先勾选要导出的记录"); return; }
    try {
      for (const id of checkedIds) await recognitionService.exportToExcel(id);
    } catch { alert("导出失败，请重试"); }
  };

  const selectClass = "appearance-none bg-muted/60 border border-border rounded-lg px-3 py-2 text-[13px] pr-8 focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all";

  const getDisplayData = (r: RecordItem) =>
    buildListDisplayData(r.summary || {}, r.original_filename, r.status, r.invoice_type, r.created_at, r.confidence_score);

  return (
    <div className="h-full flex flex-col">
      {/* Header & Filters */}
      <div className={`${isMobile ? "px-4 py-4" : "px-6 py-5"} border-b border-border space-y-3 bg-card/50`}>
        <div className="flex items-center gap-3">
          <div className={`${isMobile ? "w-8 h-8" : "w-9 h-9"} rounded-xl bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center shrink-0`}>
            <List className={`${isMobile ? "w-4 h-4" : "w-5 h-5"} text-blue-600 dark:text-blue-400`} />
          </div>
          <div className="flex-1 min-w-0">
            <h2 className={`${isMobile ? "text-[15px]" : "text-[17px]"}`}>{isTrainTicket ? "高铁票" : "发票"}列表</h2>
            {!isMobile && <p className="text-[12px] text-muted-foreground mt-0.5">查询、导出、管理所有记录</p>}
          </div>
          <button onClick={() => loadRecords()} disabled={loading}
            className={`flex items-center gap-1.5 ${isMobile ? "px-3 py-1.5 text-[13px]" : "px-4 py-2 text-[13px]"} border border-border rounded-xl hover:bg-accent transition-all duration-200 disabled:opacity-50 shrink-0`}>
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            {isMobile ? "" : loading ? "加载中..." : "刷新"}
          </button>
          <button onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center gap-1.5 ${isMobile ? "px-3 py-1.5 text-[13px]" : "px-4 py-2 text-[13px]"} border border-border rounded-xl hover:bg-accent transition-all duration-200 shrink-0`}>
            <SlidersHorizontal className="w-4 h-4" />
            {!isMobile && (showAdvanced ? "收起" : "筛选")}
            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <input value={filterKeyword} onChange={(e) => setFilterKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="搜索文件名"
            className={`bg-muted/60 border border-border rounded-lg px-3 py-2 text-[13px] ${isMobile ? "flex-1 min-w-0" : "w-56"} focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all`} />
          {showAdvanced && (
            <div className="relative">
              <select value={filterProcess} onChange={(e) => setFilterProcess(e.target.value)} className={selectClass}>
                <option value="">处理状态</option>
                <option>已完成</option>
                <option>失败</option>
              </select>
              <ChevronDown className="w-4 h-4 absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            </div>
          )}
          <button onClick={handleSearch}
            className="flex items-center gap-1.5 px-3 py-2 text-[13px] bg-primary text-primary-foreground rounded-lg hover:shadow-md transition-all">
            <Search className="w-4 h-4" /> {isMobile ? "" : "搜索"}
          </button>
          <button onClick={resetFilters}
            className="flex items-center gap-1.5 px-3 py-2 text-[13px] border border-border rounded-lg hover:bg-accent transition-all">
            <RotateCcw className="w-4 h-4" /> {isMobile ? "" : "重置"}
          </button>
        </div>

        {/* Batch actions */}
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={toggleAll} className="px-3 py-1.5 text-[12px] border border-border rounded-lg hover:bg-accent transition-all">
            {headerChecked ? "取消全选" : "全选"}
          </button>
          {!isMobile && (
            <button onClick={() => setRecords((p) => p.map((r) => ({ ...r, checked: false })))}
              className="px-3 py-1.5 text-[12px] border border-border rounded-lg hover:bg-accent transition-all">清空</button>
          )}
          <div className="w-px h-4 bg-border" />
          <button onClick={handleExportCSV} className="flex items-center gap-1 px-2.5 py-1.5 text-[12px] border border-border rounded-lg hover:bg-accent transition-all"><Download className="w-3.5 h-3.5" /> CSV</button>
          <button onClick={handleExportExcel} className="flex items-center gap-1 px-2.5 py-1.5 text-[12px] border border-border rounded-lg hover:bg-accent transition-all"><Download className="w-3.5 h-3.5" /> Excel</button>
          {checkedCount > 0 && (
            <>
              <div className="w-px h-4 bg-border" />
              <button onClick={handleBatchDelete}
                className="flex items-center gap-1 px-2.5 py-1.5 text-[12px] border border-destructive/30 text-destructive rounded-lg hover:bg-destructive/10 transition-all">
                <Trash2 className="w-3.5 h-3.5" /> 删除({checkedCount})
              </button>
            </>
          )}
          <span className="ml-auto text-[12px] text-muted-foreground">共 {total} 条</span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {isMobile ? (
          /* Mobile: Card list */
          <div className="p-4 space-y-3">
            {records.length === 0 && !loading && <div className="text-center py-16 text-[14px] text-muted-foreground">无匹配结果</div>}
            {records.map((r) => {
              const data = getDisplayData(r);
              return (
                <div key={r.id} className="bg-card rounded-xl border border-border p-4 space-y-2.5">
                  <div className="flex items-start gap-3">
                    <input type="checkbox" checked={r.checked}
                      onChange={() => setRecords((p) => p.map((x) => (x.id === r.id ? { ...x, checked: !x.checked } : x)))}
                      className="mt-1 shrink-0" />
                    <div className="flex-1 min-w-0">
                      {isTrainTicket ? (
                        <>
                          <p className="text-[14px] font-medium truncate">{data.train_number} · {data.passenger_name}</p>
                          <p className="text-[12px] text-muted-foreground mt-0.5">{data.departure_station} · {data.train_date}</p>
                        </>
                      ) : (
                        <>
                          <p className="text-[14px] font-medium truncate">{data.filename}</p>
                          <p className="text-[12px] text-muted-foreground mt-0.5 truncate">{data.invoice_number} · {data.invoice_date}</p>
                        </>
                      )}
                    </div>
                    <TaskStatusBadge status={r.status as any} />
                  </div>

                  <div className="flex items-center gap-3 text-[12px] pl-7">
                    {isTrainTicket ? (
                      <span className="text-primary font-medium">{data.ticket_price}</span>
                    ) : (
                      <>
                        <span className="text-muted-foreground truncate flex-1">{data.buyer_name}</span>
                        <span className="text-primary font-medium shrink-0">{data.total_amount}</span>
                      </>
                    )}
                    {data.deductible_tax && data.deductible_tax !== "-" && (
                      <span className="text-emerald-600 dark:text-emerald-400 shrink-0">抵扣 {data.deductible_tax}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2 pl-7">
                    <ConfidenceBadge score={data.confidence_score} />
                    <span className="text-[11px] text-muted-foreground ml-auto">{data.created_at}</span>
                  </div>

                  <div className="flex items-center gap-2 pt-1 pl-7">
                    <button onClick={() => handleViewDetail(r)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] border border-border rounded-lg hover:bg-accent transition-all">
                      <Eye className="w-3.5 h-3.5" /> 详情
                    </button>
                    <button onClick={() => handleDelete(r.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] border border-destructive/30 text-destructive rounded-lg hover:bg-destructive/10 transition-all">
                      <Trash2 className="w-3.5 h-3.5" /> 删除
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Desktop: Table */
          <>
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/40 sticky top-0 z-10">
                  <th className="w-12 px-4 py-3.5">
                    <input type="checkbox" checked={headerChecked} onChange={toggleAll} />
                  </th>
                  {(isTrainTicket
                    ? ["电子客票号", "车次", "乘客", "起始站", "发车日期", "票价", "可抵扣税额", "状态", "置信度", "创建时间", "操作"]
                    : ["文件名", "发票号码", "开票日期", "购买方", "销售方", "金额", "可抵扣税额", "状态", "置信度", "创建时间", "操作"]
                  ).map((h) => (
                    <th key={h} className="text-left px-4 py-3.5 text-[13px] text-muted-foreground whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {records.map((r) => {
                  const data = getDisplayData(r);
                  return (
                    <tr key={r.id} className="border-b border-border hover:bg-accent/40 transition-colors duration-150">
                      <td className="px-4 py-3.5">
                        <input type="checkbox" checked={r.checked}
                          onChange={() => setRecords((p) => p.map((x) => (x.id === r.id ? { ...x, checked: !x.checked } : x)))} />
                      </td>
                      {isTrainTicket ? (
                        <>
                          <td className="px-4 py-3.5 text-[13px] font-mono">{data.ticket_id}</td>
                          <td className="px-4 py-3.5"><span className="text-[12px] px-2.5 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">{data.train_number}</span></td>
                          <td className="px-4 py-3.5 text-[13px]">{data.passenger_name}</td>
                          <td className="px-4 py-3.5 text-[13px]">{data.departure_station}</td>
                          <td className="px-4 py-3.5 text-[13px] text-muted-foreground">{data.train_date}</td>
                          <td className="px-4 py-3.5 text-[13px] text-primary font-medium">{data.ticket_price}</td>
                        </>
                      ) : (
                        <>
                          <td className="px-4 py-3.5 text-[13px] max-w-[200px] truncate" title={data.filename}>{data.filename}</td>
                          <td className="px-4 py-3.5 text-[13px] font-mono">{data.invoice_number}</td>
                          <td className="px-4 py-3.5 text-[13px]">{data.invoice_date}</td>
                          <td className="px-4 py-3.5 text-[13px] max-w-[150px] truncate" title={data.buyer_name}>{data.buyer_name}</td>
                          <td className="px-4 py-3.5 text-[13px] max-w-[150px] truncate" title={data.seller_name}>{data.seller_name}</td>
                          <td className="px-4 py-3.5 text-[13px] text-primary font-medium">{data.total_amount}</td>
                        </>
                      )}
                      <td className="px-4 py-3.5 text-[13px] text-emerald-600 dark:text-emerald-400">{data.deductible_tax}</td>
                      <td className="px-4 py-3.5"><TaskStatusBadge status={r.status as any} /></td>
                      <td className="px-4 py-3.5 text-[13px]">
                        <ConfidenceBadge score={data.confidence_score} />
                      </td>
                      <td className="px-4 py-3.5 text-[12px] text-muted-foreground whitespace-nowrap">{data.created_at}</td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-1">
                          <button onClick={() => handleViewDetail(r)} className="p-1.5 hover:bg-accent rounded-lg transition-all" title="详情"><Eye className="w-4 h-4 text-muted-foreground" /></button>
                          <button onClick={() => handleDelete(r.id)} className="p-1.5 hover:bg-destructive/10 rounded-lg transition-all" title="删除"><Trash2 className="w-4 h-4 text-muted-foreground hover:text-destructive" /></button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {records.length === 0 && !loading && <div className="text-center py-20 text-[14px] text-muted-foreground">无匹配结果</div>}
          </>
        )}
      </div>

      <Pagination
        page={page} totalPages={totalPages} pageSize={pageSize} total={total}
        onPageChange={(p) => setPage(p)}
        onPageSizeChange={(s) => { setPageSize(s); setPage(1); }}
      />

      {/* Detail Modal */}
      {modal && modal.record && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setModal(null)}>
          <div className={`bg-card rounded-2xl border border-border shadow-2xl ${isMobile ? "mx-4 w-full max-h-[90vh]" : "w-[700px] max-h-[80vh]"} overflow-auto`} onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-5 border-b border-border flex items-center justify-between sticky top-0 bg-card z-10">
              <div className="min-w-0 flex-1">
                <h3 className="text-[17px]">发票详情</h3>
                <p className="text-[12px] text-muted-foreground mt-0.5 truncate">{modal.record.original_filename}</p>
              </div>
              <button onClick={() => setModal(null)} className="p-1.5 hover:bg-accent rounded-lg transition-all shrink-0 ml-3"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              {modal.detail && modal.detail.items && modal.detail.items.length > 0 ? (
                <div className="space-y-3">
                  <div className="max-h-[400px] overflow-auto space-y-3">
                    {modal.detail.items.map((item, idx) => {
                      const detailedFields = extractDetailedFields(item);
                      return (
                        <div key={item.id} className="bg-muted/30 rounded-xl p-4 border border-border/50">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-[13px] font-medium text-muted-foreground">
                              {item.page_number ? `第 ${item.page_number} 页` : modal.detail!.items.length > 1 ? `项目 ${idx + 1}` : "识别结果"}
                            </span>
                            <ReviewStatusBadge status={item.review_status} />
                          </div>
                          <InvoiceFieldDisplay fields={detailedFields} invoiceType={modal.record?.invoice_type as string} />
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-[13px] text-muted-foreground">暂无识别结果</div>
              )}

              <details className="group">
                <summary className="text-[13px] text-muted-foreground cursor-pointer hover:text-foreground transition-colors flex items-center gap-1.5">
                  <ChevronDown className="w-3.5 h-3.5 group-open:rotate-180 transition-transform" />
                  任务信息
                </summary>
                <div className="mt-3 space-y-2 pl-5">
                  {([
                    ["文件类型", modal.record.file_type || "-"],
                    ["发票类型", modal.record.invoice_type || "-"],
                    ["状态", TASK_STATUS_LABELS[modal.record.status as TaskStatus] || modal.record.status || "-"],
                    ["创建时间", formatBeijingTime(modal.record.created_at)],
                    ["完成时间", modal.record.finished_at ? formatBeijingTime(modal.record.finished_at) : "-"],
                  ] as [string, string][]).map(([l, v]) => (
                    <div key={l} className="flex justify-between text-[13px] py-1.5 border-b border-border/30">
                      <span className="text-muted-foreground">{l}</span><span>{v}</span>
                    </div>
                  ))}
                  {modal.record.error_message && (
                    <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-lg p-3">
                      <p className="text-[13px] text-red-600 dark:text-red-400">{modal.record.error_message}</p>
                    </div>
                  )}
                </div>
              </details>
            </div>
            <div className="px-6 py-5 border-t border-border flex gap-3 justify-end sticky bottom-0 bg-card">
              <button onClick={() => setModal(null)} className="px-5 py-2.5 text-[14px] border border-border rounded-xl hover:bg-accent transition-all">关闭</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
