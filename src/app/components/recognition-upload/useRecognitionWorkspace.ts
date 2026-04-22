/**
 * 识别上传工作区核心 hook
 * 管理文件列表（服务端分页）、上传、轮询、导出等全部状态与副作用
 */
import { useState, useRef, useEffect, useCallback } from "react";
import {
  recognitionService,
  type InvoiceType,
  type RecognitionMode,
} from "../../../lib/services/recognition";
import {
  recoverTaskDetail,
  pollTaskStatus as pollTaskStatusHelper,
  mapTaskStatusToFileStatus,
} from "../../../lib/helpers/recognitionTask";
import {
  getBestResultItem,
  extractDetailedFields,
} from "../../../lib/helpers/recognitionResult";
import type { UploadedFile } from "./types";

export type MobileTab = "upload" | "preview" | "result";

const DEFAULT_PAGE_SIZE = 10;

export function useRecognitionWorkspace(activeMenu: string) {
  /* ---- 服务端分页状态 ---- */
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [restoring, setRestoring] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(DEFAULT_PAGE_SIZE);
  const [total, setTotal] = useState(0);

  /* ---- 本地新上传（尚未入库或正在处理中）的临时条目 ---- */
  const [localUploads, setLocalUploads] = useState<UploadedFile[]>([]);

  const [mobileTab, setMobileTab] = useState<MobileTab>("upload");
  const [currentFileId, setCurrentFileId] = useState<number | null>(null);
  const [recognitionMode, setRecognitionMode] = useState<RecognitionMode>("ai");
  const [uploading, setUploading] = useState(false);
  const [viewMode, setViewMode] = useState<"structured" | "json">("structured");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervals = useRef<Map<number, NodeJS.Timeout>>(new Map());

  const isTrainTicket = activeMenu === "train";
  const invoiceType: InvoiceType = isTrainTicket ? "railway_ticket" : "vat_normal";

  const totalPages = Math.ceil(total / pageSize) || 1;

  /**
   * 合并视图：本地新上传条目（置顶） + 服务端分页条目（去重）
   */
  const mergedFiles = (() => {
    const serverTaskIds = new Set(files.map((f) => f.taskId));
    const pendingLocal = localUploads.filter(
      (l) => l.taskId === 0 || !serverTaskIds.has(l.taskId)
    );
    return [...pendingLocal, ...files];
  })();

  const currentFile = mergedFiles.find((f) => f.id === currentFileId);

  /**
   * 用 ref 持有 loadPage 的最新引用，打破 loadPage ↔ pollTask 循环依赖
   */
  const loadPageRef = useRef<(p?: number) => Promise<void>>();

  // ---- 服务端分页加载 ----
  const loadPage = useCallback(async (p?: number) => {
    const targetPage = p ?? page;
    try {
      const response = await recognitionService.getTasksPaginated({
        invoiceType,
        page: targetPage,
        pageSize,
      });
      if (response.success && response.data) {
        const serverFiles: UploadedFile[] = response.data.items.map((task) => {
          const ext = (task.original_filename.split('.').pop() || '').toLowerCase();
          const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'tif'];
          let fileType = '';
          if (imageExts.includes(ext)) {
            fileType = `image/${ext === 'jpg' ? 'jpeg' : ext === 'tif' ? 'tiff' : ext}`;
          } else if (ext === 'pdf') {
            fileType = 'application/pdf';
          }
          return {
            id: task.id,
            taskId: task.id,
            name: task.original_filename,
            status: mapTaskStatusToFileStatus(task.status as any),
            selected: false,
            progress: task.progress,
            items: [],
            fileUrl: recognitionService.getPreviewUrl(task.id),
            fileType,
            fromBackend: true,
            errorMessage: task.error_message,
          };
        });
        setFiles(serverFiles);
        setTotal(response.data.total);

        // 清理已入库的 localUploads
        const serverIds = new Set(serverFiles.map((f) => f.taskId));
        setLocalUploads((prev) =>
          prev.filter((l) => l.taskId === 0 || !serverIds.has(l.taskId))
        );

        // 对仍在处理中的任务启动轮询
        serverFiles.forEach((f) => {
          if ((f.status === "processing" || f.status === "queued") && !pollingIntervals.current.has(f.taskId)) {
            const interval = setInterval(() => pollTask(f.taskId), 2000);
            pollingIntervals.current.set(f.taskId, interval);
            pollTask(f.taskId);
          }
        });
      }
    } catch (error) {
      console.error("加载任务列表失败:", error);
    }
  }, [invoiceType, page, pageSize]);

  // 保持 ref 始终指向最新的 loadPage
  loadPageRef.current = loadPage;

  // ---- polling（通过 ref 调用 loadPage，避免循环依赖） ----
  const pollTask = useCallback(async (taskId: number) => {
    await pollTaskStatusHelper(
      taskId,
      (updatedTask) => {
        const newStatus = mapTaskStatusToFileStatus(updatedTask.status as any);
        const update = (f: UploadedFile): UploadedFile =>
          f.taskId === taskId
            ? { ...f, status: newStatus, progress: updatedTask.progress, items: updatedTask.items || f.items, errorMessage: updatedTask.error_message }
            : f;
        setFiles((prev) => prev.map(update));
        setLocalUploads((prev) => prev.map(update));
      },
      () => {
        const interval = pollingIntervals.current.get(taskId);
        if (interval) {
          clearInterval(interval);
          pollingIntervals.current.delete(taskId);
        }
        // 任务完成后刷新当前页
        loadPageRef.current?.();
      }
    );
  }, []);

  // ---- 初始加载 + activeMenu 切换 ----
  useEffect(() => {
    setRestoring(true);
    setPage(1);
    setLocalUploads([]);
    const init = async () => {
      try {
        await loadPage(1);
      } finally {
        setRestoring(false);
      }
    };
    init();
  }, [invoiceType]);

  // ---- 翻页 ----
  useEffect(() => {
    loadPage();
  }, [page]);

  // cleanup polling on unmount
  useEffect(() => {
    return () => {
      pollingIntervals.current.forEach((interval) => clearInterval(interval));
      pollingIntervals.current.clear();
    };
  }, []);

  // ---- load task detail for current file ----
  useEffect(() => {
    const loadTaskDetail = async () => {
      if (currentFile && currentFile.status === "done" && currentFile.items.length === 0 && currentFile.taskId > 0) {
        try {
          const detail = await recoverTaskDetail(currentFile.taskId);
          if (detail) {
            const updateItems = (f: UploadedFile): UploadedFile =>
              f.id === currentFile.id ? { ...f, items: detail.items || [] } : f;
            setFiles((prev) => prev.map(updateItems));
            setLocalUploads((prev) => prev.map(updateItems));
          }
        } catch (error) {
          console.error("加载任务详情失败:", error);
        }
      }
    };
    loadTaskDetail();
  }, [currentFileId]);

  // ---- handlers ----
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(Array.from(e.target.files || []));
  }, []);

  const handleUpload = useCallback(async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);

    for (const file of selectedFiles) {
      const tempId = Date.now() + Math.random();
      const fileUrl = URL.createObjectURL(file);

      const tempFile: UploadedFile = {
        id: tempId,
        taskId: 0,
        name: file.name,
        status: "uploading",
        selected: false,
        progress: 0,
        items: [],
        fileUrl,
        fileType: file.type,
      };
      setLocalUploads((prev) => [tempFile, ...prev]);

      try {
        const response = await recognitionService.createTask(file, invoiceType, recognitionMode);

        if (response.success && response.data) {
          const taskId = response.data.id;
          setLocalUploads((prev) =>
            prev.map((f) =>
              f.id === tempId ? { ...f, taskId, status: "processing" } : f
            )
          );
          setTotal((prev) => prev + 1);
          const interval = setInterval(() => pollTask(taskId), 2000);
          pollingIntervals.current.set(taskId, interval);
          pollTask(taskId);
        } else {
          setLocalUploads((prev) =>
            prev.map((f) =>
              f.id === tempId
                ? { ...f, status: "failed", errorMessage: response.error || "上传失败" }
                : f
            )
          );
        }
      } catch {
        setLocalUploads((prev) =>
          prev.map((f) =>
            f.id === tempId
              ? { ...f, status: "failed", errorMessage: "网络错误" }
              : f
          )
        );
      }
    }

    setUploading(false);
    setSelectedFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, [selectedFiles, invoiceType, recognitionMode, pollTask]);

  const handleSelectAll = useCallback(() => {
    const toggle = (prev: UploadedFile[]) => {
      const selectable = prev.filter(
        (f) => f.status !== "uploading" && f.status !== "queued" && f.status !== "processing"
      );
      const allSelected = selectable.length > 0 && selectable.every((f) => f.selected);
      return prev.map((f) =>
        f.status !== "uploading" && f.status !== "queued" && f.status !== "processing"
          ? { ...f, selected: !allSelected }
          : f
      );
    };
    setFiles(toggle);
    setLocalUploads(toggle);
  }, []);

  const handleBatchDelete = useCallback(async () => {
    const serverIds = mergedFiles
      .filter((f) => f.selected && f.taskId > 0)
      .map((f) => f.taskId);

    // 先乐观移除
    setFiles((prev) => prev.filter((f) => !f.selected));
    setLocalUploads((prev) => prev.filter((f) => !f.selected));
    if (currentFile?.selected) setCurrentFileId(null);

    // 调服务端物理删除
    if (serverIds.length > 0) {
      try {
        await recognitionService.batchDeleteTasks(serverIds);
      } catch {
        console.error("批量删除失败");
      }
      // 刷新当前页
      loadPageRef.current?.();
    }
  }, [currentFile, mergedFiles]);

  const handleExportCSV = useCallback(async () => {
    const selectedDoneFiles = mergedFiles.filter((f) => f.selected && f.status === "done");
    if (selectedDoneFiles.length === 0) { alert("请先勾选已完成的文件"); return; }
    try {
      for (const file of selectedDoneFiles) {
        await recognitionService.exportToCsv(file.taskId);
      }
    } catch {
      alert("导出失败，请重试");
    }
  }, [mergedFiles]);

  const handleExportExcel = useCallback(async () => {
    const selectedDoneFiles = mergedFiles.filter((f) => f.selected && f.status === "done");
    if (selectedDoneFiles.length === 0) { alert("请先勾选已完成的文件"); return; }
    try {
      for (const file of selectedDoneFiles) {
        await recognitionService.exportToExcel(file.taskId);
      }
    } catch {
      alert("导出失败，请重试");
    }
  }, [mergedFiles]);

  const handleRetryFailed = useCallback(async () => {
    const failedFiles = mergedFiles.filter((f) => f.status === "failed");

    for (const file of failedFiles) {
      const markUploading = (prev: UploadedFile[]) =>
        prev.map((f) => (f.id === file.id ? { ...f, status: "uploading" as const } : f));
      setFiles(markUploading);
      setLocalUploads(markUploading);

      if (file.fileUrl) {
        try {
          const blob = await fetch(file.fileUrl).then((r) => r.blob());
          const newFile = new File([blob], file.name, { type: file.fileType });
          const response = await recognitionService.createTask(newFile, invoiceType, recognitionMode);

          if (response.success && response.data) {
            const taskId = response.data.id;
            const markProcessing = (prev: UploadedFile[]) =>
              prev.map((f) =>
                f.id === file.id ? { ...f, taskId, status: "processing" as const } : f
              );
            setFiles(markProcessing);
            setLocalUploads(markProcessing);
            const interval = setInterval(() => pollTask(taskId), 2000);
            pollingIntervals.current.set(taskId, interval);
            pollTask(taskId);
          } else {
            const markFailed = (prev: UploadedFile[]) =>
              prev.map((f) =>
                f.id === file.id
                  ? { ...f, status: "failed" as const, errorMessage: response.error || "重试失败" }
                  : f
              );
            setFiles(markFailed);
            setLocalUploads(markFailed);
          }
        } catch {
          const markFailed = (prev: UploadedFile[]) =>
            prev.map((f) =>
              f.id === file.id ? { ...f, status: "failed" as const, errorMessage: "重试失败" } : f
            );
          setFiles(markFailed);
          setLocalUploads(markFailed);
        }
      }
    }
  }, [mergedFiles, invoiceType, recognitionMode, pollTask]);

  const handleFileClick = useCallback((id: number) => setCurrentFileId(id), []);
  const handleFileToggle = useCallback((id: number) => {
    const toggle = (prev: UploadedFile[]) =>
      prev.map((f) => (f.id === id ? { ...f, selected: !f.selected } : f));
    setFiles(toggle);
    setLocalUploads(toggle);
  }, []);
  const handleFileRemove = useCallback((id: number) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
    setLocalUploads((prev) => prev.filter((f) => f.id !== id));
    setCurrentFileId((prev) => (prev === id ? null : prev));
  }, []);

  const handlePageChange = useCallback((p: number) => {
    setPage(p);
  }, []);

  // ---- derived ----
  const bestResultItem = currentFile?.items ? getBestResultItem(currentFile.items) : null;
  const detailedFields = extractDetailedFields(bestResultItem);
  const currentResult = bestResultItem?.reviewed_result || bestResultItem?.original_result;
  const currentResultJson = currentResult ? JSON.stringify(currentResult, null, 2) : "";

  return {
    // state
    restoring,
    files: mergedFiles,
    currentFileId,
    currentFile,
    recognitionMode,
    uploading,
    selectedFiles,
    viewMode,
    isTrainTicket,
    invoiceType,
    fileInputRef,
    mobileTab,
    setMobileTab,
    // pagination
    page,
    pageSize,
    total,
    totalPages,
    onPageChange: handlePageChange,
    // derived
    detailedFields,
    currentResultJson,
    // actions
    setRecognitionMode,
    setViewMode,
    handleFileSelect,
    handleUpload,
    handleSelectAll,
    handleBatchDelete,
    handleExportCSV,
    handleExportExcel,
    handleRetryFailed,
    handleFileClick,
    handleFileToggle,
    handleFileRemove,
  };
}
