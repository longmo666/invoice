/**
 * 识别任务状态管理 helper
 *
 * 职责：状态映射、轮询、任务详情恢复
 * 数据获取统一走 recognitionService，不在此处直接调 API
 */

import { recognitionService, type RecognitionTaskDetail, type TaskStatus } from '../services/recognition';

/**
 * 映射后端任务状态到前端文件状态
 */
export function mapTaskStatusToFileStatus(status: TaskStatus): 'queued' | 'processing' | 'done' | 'failed' {
  const statusMap: Record<TaskStatus, 'queued' | 'processing' | 'done' | 'failed'> = {
    uploading: 'queued',
    processing: 'processing',
    done: 'done',
    failed: 'failed',
  };
  return statusMap[status] || 'queued';
}

/**
 * 恢复单个任务的完整状态（包括详情和 items）
 */
export async function recoverTaskDetail(taskId: number): Promise<RecognitionTaskDetail | null> {
  try {
    const response = await recognitionService.getTaskDetail(taskId);
    if (response.success && response.data) {
      return response.data;
    }
    return null;
  } catch (error) {
    console.error('Recover task detail error:', error);
    return null;
  }
}

/**
 * 轮询任务状态
 */
export async function pollTaskStatus(
  taskId: number,
  onUpdate: (task: RecognitionTaskDetail) => void,
  onComplete: () => void
): Promise<void> {
  try {
    const response = await recognitionService.getTaskDetail(taskId);
    if (response.success && response.data) {
      onUpdate(response.data);

      if (response.data.status === 'done' || response.data.status === 'failed') {
        onComplete();
      }
    }
  } catch (error) {
    console.error('Poll task status error:', error);
  }
}
