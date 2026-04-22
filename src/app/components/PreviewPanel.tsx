/**
 * 文件预览面板（从 UploadRecognition 拆分）
 */
import {
  Upload,
  Clock,
  Loader2,
  CheckCircle2,
  XCircle,
  RefreshCw,
  FileImage,
  Eye,
} from "lucide-react";
import HelpTip from "./HelpTip";
import FilePreview from "./FilePreview";
import type { UploadedFile } from "./recognition-upload/types";
import { statusConfig } from "./recognition-upload/types";

interface PreviewPanelProps {
  files: UploadedFile[];
  currentFile: UploadedFile | undefined;
  onRetryFailed: () => void;
  isMobile?: boolean;
}

export default function PreviewPanel({ files, currentFile, onRetryFailed, isMobile }: PreviewPanelProps) {
  const failedCount = files.filter((f) => f.status === "failed").length;
  const doneCount = files.filter((f) => f.status === "done").length;
  const processingCount = files.filter((f) => f.status === "processing").length;
  const queuedCount = files.filter((f) => f.status === "queued").length;
  const uploadingCount = files.filter((f) => f.status === "uploading").length;

  return (
    <div className={`flex flex-col ${isMobile ? "h-full" : "flex-1 min-w-0"} bg-background`} onClick={(e) => e.stopPropagation()}>
      <div className={`${isMobile ? "px-4 py-3" : "px-6 py-4"} border-b border-border flex items-center gap-3 bg-card/50`}>
        <div className="w-7 h-7 rounded-lg bg-muted flex items-center justify-center">
          <Eye className="w-4 h-4 text-muted-foreground" />
        </div>
        <h3 className="text-[15px] flex-1 truncate">{currentFile ? currentFile.name : "文件预览"}</h3>
        {currentFile && (
          <span className={`text-[12px] px-2.5 py-1 rounded-full ${statusConfig[currentFile.status].bg} ${statusConfig[currentFile.status].color}`}>
            {statusConfig[currentFile.status].label}
          </span>
        )}
      </div>

      {/* Stats bar */}
      {files.length > 0 && (
        <div className={`${isMobile ? "px-4 py-2" : "px-6 py-3"} border-b border-border flex items-center gap-3 flex-wrap bg-card/30`}>
          <div className="flex items-center gap-4 text-[12px] flex-wrap">
            {uploadingCount > 0 && <span className="flex items-center gap-1 text-blue-600 dark:text-blue-400"><Upload className="w-3 h-3" /> 上传 {uploadingCount}</span>}
            {queuedCount > 0 && <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400"><Clock className="w-3 h-3" /> 排队 {queuedCount}</span>}
            {processingCount > 0 && <span className="flex items-center gap-1 text-blue-600 dark:text-blue-400"><Loader2 className="w-3 h-3 animate-spin" /> 处理 {processingCount}</span>}
            {doneCount > 0 && <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400"><CheckCircle2 className="w-3 h-3" /> 完成 {doneCount}</span>}
            {failedCount > 0 && <span className="flex items-center gap-1 text-red-600 dark:text-red-400"><XCircle className="w-3 h-3" /> 失败 {failedCount}</span>}
          </div>
          {failedCount > 0 && (
            <button onClick={onRetryFailed}
              className="ml-auto flex items-center gap-1.5 text-[12px] text-primary hover:text-primary/80 transition-colors">
              <RefreshCw className="w-3 h-3" /> 重试失败
            </button>
          )}
        </div>
      )}

      {/* Preview area */}
      <div className="flex-1 overflow-auto">
        {!currentFile ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4">
            <div className={`${isMobile ? "w-14 h-14 mb-3" : "w-20 h-20 mb-4"} mx-auto rounded-2xl bg-muted flex items-center justify-center`}>
              <FileImage className={`${isMobile ? "w-7 h-7" : "w-10 h-10"} text-muted-foreground/25`} />
            </div>
            <p className="text-[15px] text-muted-foreground mb-1">选择文件预览</p>
            <p className="text-[12px] text-muted-foreground/50">点击左侧文件列表查看</p>
          </div>
        ) : (
          <div className="h-full">
            <FilePreview
              fileUrl={currentFile.fileUrl}
              fileType={currentFile.fileType}
              fileName={currentFile.name}
              taskId={currentFile.taskId}
            />
          </div>
        )}
      </div>
    </div>
  );
}
