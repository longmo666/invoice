/**
 * 共享状态 Badge 组件
 *
 * 收口所有组件中重复的状态/置信度 badge 渲染逻辑
 */

import type { TaskStatus } from "../../lib/services/recognition";
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS } from "../../lib/services/recognition";
import { mapReviewStatus } from "../../lib/helpers/format";

// ==================== 任务处理状态 Badge ====================

export function TaskStatusBadge({ status }: { status: TaskStatus }) {
  const label = TASK_STATUS_LABELS[status] || status;
  const color = TASK_STATUS_COLORS[status] || "";
  return (
    <span className={`text-[12px] px-2 py-0.5 rounded-lg whitespace-nowrap ${color}`}>
      {label}
    </span>
  );
}

// ==================== 置信度 Badge ====================

export function ConfidenceBadge({ score }: { score: number | null | undefined }) {
  if (score === null || score === undefined) {
    return <span className="text-muted-foreground">-</span>;
  }
  const cls =
    score >= 0.9
      ? "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
      : score >= 0.7
        ? "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400"
        : "bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400";
  return (
    <span className={`px-2 py-0.5 rounded-lg text-[12px] ${cls}`}>
      {(score * 100).toFixed(1)}%
    </span>
  );
}

// ==================== 复核状态 Badge ====================

export function ReviewStatusBadge({ status }: { status: string }) {
  const label = mapReviewStatus(status);
  const cls =
    status === "auto_passed"
      ? "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
      : status === "pending_review"
        ? "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400"
        : "bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400";
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full ${cls}`}>
      {label}
    </span>
  );
}
