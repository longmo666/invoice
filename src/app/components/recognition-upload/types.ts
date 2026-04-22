/**
 * 识别上传模块共享类型与常量
 * 从 UploadPanel 抽离，供 hook / shell / panel 共用
 */
import {
  Upload,
  Clock,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import type { RecognitionItem } from "../../../lib/types/recognition";

export type FileStatus = "uploading" | "queued" | "processing" | "done" | "failed";

export interface UploadedFile {
  id: number;
  taskId: number;
  name: string;
  status: FileStatus;
  selected: boolean;
  progress: number | null;
  items: RecognitionItem[];
  fileUrl?: string;
  fileType?: string;
  errorMessage?: string | null;
  fromBackend?: boolean;
}

export const statusConfig: Record<FileStatus, { label: string; color: string; bg: string; icon: any }> = {
  uploading: { label: "上传中", color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-500/10", icon: Upload },
  queued: { label: "排队中", color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-50 dark:bg-amber-500/10", icon: Clock },
  processing: { label: "处理中", color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-500/10", icon: Loader2 },
  done: { label: "已完成", color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-500/10", icon: CheckCircle2 },
  failed: { label: "失败", color: "text-red-600 dark:text-red-400", bg: "bg-red-50 dark:bg-red-500/10", icon: XCircle },
};
