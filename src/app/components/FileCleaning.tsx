import { useState, useEffect, useRef } from "react";
import {
  FolderSync,
  Upload,
  RotateCcw,
  Download,
  Loader2,
  CheckCircle2,
  Clock,
  XCircle,
  RefreshCw,
  Archive,
  FileCheck,
  Trash2,
  ChevronDown,
  AlertCircle,
} from "lucide-react";
import HelpTip from "./HelpTip";
import { useAuth } from "./AuthContext";
import { cleaningService, CleaningTaskListItem } from "../../lib/services/cleaning";
import { formatBeijingTime } from "../../lib/helpers/format";

const exportOptions = [
  { value: "image", label: "图片" },
  { value: "pdf", label: "PDF" },
  { value: "word", label: "Word" },
  { value: "excel", label: "Excel" },
  { value: "ppt", label: "PPT" },
  { value: "ofd", label: "OFD" },
  { value: "xml", label: "XML" },
];

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

type CheckableTask = CleaningTaskListItem & { checked: boolean };

export default function FileCleaning() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<CheckableTask[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [exportFormats, setExportFormats] = useState<string[]>(["image", "pdf"]);
  const [uploading, setUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [taskListOpen, setTaskListOpen] = useState(true);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadTasks();
    // 动态轮询：有活跃任务时快速轮询，否则慢速轮询
    const interval = setInterval(() => {
      loadTasks();
    }, hasActiveTasks() ? 1000 : 3000);
    return () => clearInterval(interval);
  }, [tasks]);

  const hasActiveTasks = () => {
    return tasks.some(t => t.status === 'uploading' || t.status === 'processing');
  };

  const loadTasks = async () => {
    const response = await cleaningService.getUserTasks();
    if (response.success && response.data) {
      setTasks(prev => {
        const checkedIds = new Set(prev.filter(t => t.checked).map(t => t.id));
        return response.data!.map(t => ({ ...t, checked: checkedIds.has(t.id) }));
      });
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");

    // 验证文件类型
    const ext = file.name.toLowerCase().split('.').pop();
    if (!['zip', '7z', 'rar'].includes(ext || '')) {
      setError("仅支持 zip、7z、rar 格式的压缩包");
      return;
    }

    // 验证文件大小
    if (file.size > MAX_FILE_SIZE) {
      setError(`文件大小不能超过 ${MAX_FILE_SIZE / 1024 / 1024}MB`);
      return;
    }

    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!selectedFile || exportFormats.length === 0) return;

    setError("");
    setUploading(true);

    try {
      const response = await cleaningService.createTask(selectedFile, exportFormats);
      if (response.success && response.data) {
        // 立即将新任务插入列表（显示初始状态）
        const newTask: CheckableTask = {
          id: response.data.id,
          original_filename: response.data.original_filename,
          selected_types: response.data.selected_types,
          status: response.data.status,
          progress: response.data.progress || 5,
          matched_count: 0,
          created_at: response.data.created_at,
          checked: false,
        };
        setTasks(prev => [newTask, ...prev]);

        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }

        // 不立即刷新，交给定时轮询更新，避免立刻覆盖 uploading 状态
      } else {
        setError(response.error || "上传失败");
      }
    } catch (err) {
      setError("上传失败，请重试");
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setExportFormats(["image", "pdf"]);
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadTasks();
    setTimeout(() => setRefreshing(false), 800);
  };

  const handleDownload = async (taskId: number) => {
    try {
      await cleaningService.downloadResult(taskId);
    } catch (err) {
      setError("下载失败");
    }
  };

  const handleRetry = async (taskId: number) => {
    try {
      const response = await cleaningService.retryTask(taskId);
      if (response.success) {
        await loadTasks();
      } else {
        setError(response.error || "重试失败");
      }
    } catch (err) {
      setError("重试失败");
    }
  };

  const handleDelete = async (taskId: number) => {
    if (!confirm("确定要删除这个任务吗？")) return;

    try {
      const response = await cleaningService.deleteTask(taskId);
      if (response.success) {
        await loadTasks();
      } else {
        setError(response.error || "删除失败");
      }
    } catch (err) {
      setError("删除失败");
    }
  };

  const handleBatchDelete = async () => {
    const ids = tasks.filter((t) => t.checked).map((t) => t.id);
    if (ids.length === 0) return;
    if (!confirm(`确定要删除选中的 ${ids.length} 个任务？此操作不可恢复。`)) return;
    try {
      await cleaningService.batchDeleteUserTasks(ids);
      setTasks((prev) => prev.filter((t) => !ids.includes(t.id)));
    } catch (err) {
      setError("批量删除失败");
    }
  };

  const checkedCount = tasks.filter((t) => t.checked).length;

  const statusConfig = {
    uploading: { label: "上传中", color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-500/10", icon: Loader2 },
    processing: { label: "处理中", color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-50 dark:bg-amber-500/10", icon: Clock },
    done: { label: "已完成", color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-500/10", icon: CheckCircle2 },
    failed: { label: "失败", color: "text-red-600 dark:text-red-400", bg: "bg-red-50 dark:bg-red-500/10", icon: XCircle },
  };

  const formatLabel = (types: string[]) => {
    return types.map((v) => exportOptions.find((o) => o.value === v)?.label || v).join(" + ");
  };

  return (
    <div className="p-6 space-y-6">
      {/* Upload Section */}
      <div className="bg-card rounded-2xl border border-border p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
            <FolderSync className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-[16px]">文件清洗</h3>
            <p className="text-[12px] text-muted-foreground mt-0.5">上传压缩包，自动提取指定类型文件</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-[13px] flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <div className="space-y-4">
          {/* File Input */}
          <div>
            <label className="block text-[13px] text-muted-foreground mb-2">选择压缩包</label>
            <div className="flex items-center gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept=".zip,.7z,.rar"
                onChange={handleFileSelect}
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="flex-1 px-4 py-3 rounded-xl border-2 border-dashed border-border hover:border-primary/50 bg-accent/30 cursor-pointer transition-all flex items-center gap-3"
              >
                <Archive className="w-5 h-5 text-muted-foreground" />
                <span className="text-[14px] text-muted-foreground">
                  {selectedFile ? selectedFile.name : "点击选择 zip / 7z / rar 文件（最大 100MB）"}
                </span>
              </label>
            </div>
          </div>

          {/* Export Format */}
          <div>
            <label className="block text-[13px] text-muted-foreground mb-2 flex items-center gap-2">
              导出类型
              <HelpTip content="选择需要提取的文件类型，可多选" />
            </label>
            <div className="flex flex-wrap gap-2">
              {exportOptions.map((opt) => {
                const selected = exportFormats.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    onClick={() =>
                      setExportFormats((prev) =>
                        prev.includes(opt.value) ? prev.filter((v) => v !== opt.value) : [...prev, opt.value]
                      )
                    }
                    className={`px-4 py-2 rounded-xl text-[13px] transition-all ${
                      selected
                        ? "bg-gradient-to-r from-primary to-indigo-600 text-white shadow-md"
                        : "bg-muted text-muted-foreground hover:bg-accent"
                    }`}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={handleSubmit}
              disabled={!selectedFile || exportFormats.length === 0 || uploading}
              className="flex-1 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 text-white text-[14px] hover:shadow-lg hover:shadow-amber-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  上传中...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  开始清洗
                </>
              )}
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-3 rounded-xl border border-border text-[14px] hover:bg-accent transition-all flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              重置
            </button>
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="bg-card rounded-2xl border border-border overflow-hidden">
        <button
          onClick={() => setTaskListOpen(!taskListOpen)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-accent/50 transition-all"
        >
          <div className="flex items-center gap-3">
            <FileCheck className="w-5 h-5 text-primary" />
            <span className="text-[15px]">清洗任务列表</span>
            <span className="text-[12px] text-muted-foreground">（{tasks.length} 个任务）</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleRefresh();
              }}
              className="p-2 rounded-lg hover:bg-accent transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            </button>
            <ChevronDown className={`w-5 h-5 transition-transform ${taskListOpen ? "rotate-180" : ""}`} />
          </div>
        </button>

        {taskListOpen && tasks.length > 0 && (
          <div className="px-6 py-2.5 border-t border-border bg-muted/20 flex items-center gap-2.5">
            <button
              onClick={() => setTasks(prev => {
                const allChecked = prev.every(t => t.checked);
                return prev.map(t => ({ ...t, checked: !allChecked }));
              })}
              className="px-3 py-1.5 text-[13px] border border-border rounded-lg hover:bg-accent transition-all"
            >
              {tasks.every(t => t.checked) ? "取消全选" : "全选"}
            </button>
            {checkedCount > 0 && (
              <>
                <div className="w-px h-5 bg-border" />
                <button onClick={handleBatchDelete}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] border border-destructive/30 text-destructive rounded-lg hover:bg-destructive/10 transition-all">
                  <Trash2 className="w-3.5 h-3.5" /> 删除({checkedCount})
                </button>
              </>
            )}
          </div>
        )}

        {taskListOpen && (
          <div className="border-t border-border">
            {tasks.length === 0 ? (
              <div className="px-6 py-12 text-center text-muted-foreground text-[13px]">暂无清洗任务</div>
            ) : (
              <div className="divide-y divide-border">
                {tasks.map((task) => {
                  const config = statusConfig[task.status];
                  const StatusIcon = config.icon;
                  return (
                    <div key={task.id} className="px-6 py-4 hover:bg-accent/30 transition-all">
                      <div className="flex items-start gap-4">
                        <input type="checkbox" checked={task.checked}
                          onChange={() => setTasks(prev => prev.map(t => t.id === task.id ? { ...t, checked: !t.checked } : t))}
                          className="mt-1.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <p className="text-[14px] truncate">{task.original_filename}</p>
                            <span className={`px-2.5 py-1 rounded-lg text-[11px] ${config.bg} ${config.color} flex items-center gap-1.5`}>
                              <StatusIcon className={`w-3.5 h-3.5 ${task.status === 'uploading' || task.status === 'processing' ? 'animate-spin' : ''}`} />
                              {config.label}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-[12px] text-muted-foreground">
                            <span>类型: {formatLabel(task.selected_types)}</span>
                            {task.status === 'done' && <span>匹配: {task.matched_count} 个文件</span>}
                            <span>{formatBeijingTime(task.created_at)}</span>
                          </div>
                          {(task.status === 'uploading' || task.status === 'processing' || task.status === 'done') && (
                            <div className="mt-2 flex items-center gap-2">
                              <div className="flex-1 bg-muted rounded-full h-1.5 overflow-hidden">
                                <div
                                  className={`h-full transition-all duration-300 ${
                                    task.status === 'uploading'
                                      ? 'bg-gradient-to-r from-blue-500 to-blue-600'
                                      : task.status === 'processing'
                                      ? 'bg-gradient-to-r from-amber-500 to-orange-600'
                                      : 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                                  }`}
                                  style={{ width: `${task.progress}%` }}
                                />
                              </div>
                              <span className="text-xs text-muted-foreground font-medium min-w-[3rem] text-right">
                                {task.status === 'uploading' ? '上传' : task.status === 'processing' ? '处理' : '完成'} {task.progress}%
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {task.status === 'done' && (
                            <button
                              onClick={() => handleDownload(task.id)}
                              className="p-2 rounded-lg hover:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 transition-all"
                              title="下载"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                          )}
                          {task.status === 'failed' && (
                            <button
                              onClick={() => handleRetry(task.id)}
                              className="p-2 rounded-lg hover:bg-blue-500/10 text-blue-600 dark:text-blue-400 transition-all"
                              title="重试"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(task.id)}
                            className="p-2 rounded-lg hover:bg-destructive/10 text-destructive transition-all"
                            title="删除"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
