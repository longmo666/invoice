import { useState, useEffect } from "react";
import { FolderSync, CheckCircle2, Clock, XCircle, Loader2, Trash2, AlertTriangle } from "lucide-react";
import { cleaningService, AdminCleaningTaskListItem } from "../../lib/services/cleaning";
import { formatBeijingTime } from "../../lib/helpers/format";

const statusMap: Record<string, { label: string; cls: string; Icon: any }> = {
  done: { label: "已完成", cls: "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400", Icon: CheckCircle2 },
  processing: { label: "处理中", cls: "bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400", Icon: Clock },
  failed: { label: "失败", cls: "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400", Icon: XCircle },
  uploading: { label: "上传中", cls: "bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400", Icon: Loader2 },
};

const exportOptions = [
  { value: "image", label: "图片" },
  { value: "pdf", label: "PDF" },
  { value: "word", label: "Word" },
  { value: "excel", label: "Excel" },
  { value: "ppt", label: "PPT" },
  { value: "ofd", label: "OFD" },
  { value: "xml", label: "XML" },
];

export default function AdminCleaning() {
  const [tasks, setTasks] = useState<AdminCleaningTaskListItem[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [confirmDel, setConfirmDel] = useState<number[] | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTasks();
    const interval = setInterval(() => {
      loadTasks();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadTasks = async () => {
    const response = await cleaningService.getAllTasks();
    if (response.success && response.data) {
      setTasks(response.data);
    }
  };

  const allSelected = tasks.length > 0 && tasks.every((t) => selected.has(t.id));

  const toggleAll = () => {
    if (allSelected) setSelected(new Set());
    else setSelected(new Set(tasks.map((t) => t.id)));
  };

  const doDelete = async () => {
    if (!confirmDel) return;
    setLoading(true);

    const response = await cleaningService.batchDeleteTasks(confirmDel);
    if (response.success) {
      await loadTasks();
      setSelected(new Set());
    }

    setLoading(false);
    setConfirmDel(null);
  };

  const formatLabel = (types: string[]) => {
    return types.map((v) => exportOptions.find((o) => o.value === v)?.label || v).join(" + ");
  };

  return (
    <div className="h-full flex flex-col">
      <div className="px-6 py-4 border-b border-border flex items-center gap-3 bg-card/50">
        <FolderSync className="w-5 h-5 text-primary" />
        <span className="text-[15px] flex-1">全部文件清洗任务</span>
        {selected.size > 0 && (
          <button onClick={() => setConfirmDel([...selected])}
            className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400 rounded-lg hover:shadow-sm transition-all">
            <Trash2 className="w-3.5 h-3.5" /> 删除选中 ({selected.size})
          </button>
        )}
        <span className="text-[13px] text-muted-foreground">{tasks.length} 个任务</span>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/40 sticky top-0 z-10">
              <th className="text-left px-5 py-3 w-10">
                <input type="checkbox" checked={allSelected} onChange={toggleAll} className="w-4 h-4 rounded accent-primary cursor-pointer" />
              </th>
              {["归属人", "文件名", "导出类型", "状态", "创建时间", "操作"].map((h) => (
                <th key={h} className="text-left px-5 py-3 text-[13px] text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => {
              const s = statusMap[t.status] || statusMap.done;
              return (
                <tr key={t.id} className={`border-b border-border hover:bg-accent/40 transition-colors ${selected.has(t.id) ? "bg-primary/5" : ""}`}>
                  <td className="px-5 py-3">
                    <input type="checkbox" checked={selected.has(t.id)} onChange={() => {
                      const n = new Set(selected); n.has(t.id) ? n.delete(t.id) : n.add(t.id); setSelected(n);
                    }} className="w-4 h-4 rounded accent-primary cursor-pointer" />
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="text-[12px] px-2 py-0.5 rounded-lg bg-primary/10 text-primary">{t.username || "未知"}</span>
                  </td>
                  <td className="px-5 py-3.5 text-[14px]">{t.original_filename}</td>
                  <td className="px-5 py-3.5 text-[13px] text-muted-foreground">{formatLabel(t.selected_types)}</td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center gap-1.5 text-[12px] px-2.5 py-0.5 rounded-lg ${s.cls}`}>
                      <s.Icon className={`w-3.5 h-3.5 ${t.status === "processing" || t.status === "uploading" ? "animate-spin" : ""}`} />
                      {s.label}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-[13px] text-muted-foreground">{formatBeijingTime(t.created_at)}</td>
                  <td className="px-5 py-3.5">
                    <button onClick={() => setConfirmDel([t.id])} className="p-1.5 hover:bg-red-500/10 rounded-lg"><Trash2 className="w-4 h-4 text-red-500" /></button>
                  </td>
                </tr>
              );
            })}
            {tasks.length === 0 && (
              <tr><td colSpan={7} className="text-center py-20 text-[14px] text-muted-foreground">暂无任务</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {confirmDel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setConfirmDel(null)}>
          <div className="bg-card rounded-2xl border border-border shadow-2xl w-[400px]" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-5 border-b border-border flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-red-50 dark:bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-500" />
              </div>
              <h3 className="text-[17px]">确认删除</h3>
            </div>
            <div className="p-6">
              <p className="text-[14px] text-muted-foreground">确定要删除 <span className="text-foreground">{confirmDel.length}</span> 个清洗任务吗？此操作不可撤销。</p>
            </div>
            <div className="px-6 py-5 border-t border-border flex justify-end gap-3">
              <button onClick={() => setConfirmDel(null)} disabled={loading} className="px-4 py-2 text-[14px] border border-border rounded-xl hover:bg-accent transition-all disabled:opacity-50">取消</button>
              <button onClick={doDelete} disabled={loading} className="px-4 py-2 text-[14px] bg-red-500 text-white rounded-xl hover:bg-red-600 hover:shadow-md transition-all disabled:opacity-50 flex items-center gap-2">
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                确认删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
