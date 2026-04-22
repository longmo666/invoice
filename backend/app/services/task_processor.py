"""
识别任务后台处理器

从 recognition_service.py 拆分，负责任务的后台异步处理流程
"""
import threading
import asyncio
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.recognition_task import TaskStatus
from app.models.recognition_item import RecognitionItem, ReviewStatus
from app.repositories.recognition_task import RecognitionTaskRepository
from app.repositories.recognition_item import RecognitionItemRepository
from app.core.exceptions import NotFoundException
from app.services.recognition.recognition_orchestrator import RecognitionOrchestrator
from app.services.recognition.confidence_scorer import ConfidenceScorer

# 置信度阈值：低于此值进入人工复核
CONFIDENCE_THRESHOLD = 0.90


class TaskProcessor:
    """识别任务后台处理器"""

    @staticmethod
    def start_processing(task_id: int, upload_path: Path):
        """启动后台处理线程"""
        thread = threading.Thread(
            target=TaskProcessor._process_wrapper,
            args=(task_id, upload_path),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def _process_wrapper(task_id: int, upload_path: Path):
        """线程安全的处理包装器"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(TaskProcessor._process(task_id, upload_path))
        except Exception as e:
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                repo = RecognitionTaskRepository(db)
                repo.mark_failed(task_id, str(e))
            finally:
                db.close()

    @staticmethod
    async def _process(task_id: int, upload_path: Path):
        """执行识别任务的完整处理流程"""
        from app.db.session import SessionLocal
        db = SessionLocal()

        try:
            task_repo = RecognitionTaskRepository(db)
            item_repo = RecognitionItemRepository(db)

            # 获取任务
            task = task_repo.get_by_id(task_id)
            if not task:
                raise NotFoundException("任务不存在")

            # 清理旧的识别结果（重试场景）
            existing_items = item_repo.get_by_task(task_id)
            if existing_items:
                for item in existing_items:
                    db.delete(item)
                db.commit()

            # 更新状态为处理中
            task_repo.update_progress(task_id, 10, TaskStatus.PROCESSING)

            # 创建编排器并执行识别流程
            orchestrator = RecognitionOrchestrator(db)
            results = await orchestrator.execute(
                file_path=upload_path,
                file_type=task.file_type.value,
                invoice_type=task.invoice_type.value,
                recognition_mode=task.recognition_mode.value,
            )

            # 处理识别结果
            total_items = len(results)
            success_count = 0
            failed_count = 0

            for idx, result_data in enumerate(results):
                try:
                    # 更新进度
                    progress = 10 + int(((idx + 1) / total_items) * 80)
                    task_repo.update_progress(task_id, progress)

                    # 计算置信度分数
                    conf_score, conf_reason = ConfidenceScorer.score(
                        task.invoice_type.value, result_data["result"]
                    )
                    final_score = result_data.get("confidence_score") or conf_score

                    # 根据置信度决定复核状态
                    review_status = (
                        ReviewStatus.AUTO_PASSED
                        if final_score >= CONFIDENCE_THRESHOLD
                        else ReviewStatus.PENDING_REVIEW
                    )

                    # 创建识别结果项
                    item = RecognitionItem(
                        task_id=task_id,
                        page_number=result_data.get("page_number"),
                        item_index=result_data["item_index"],
                        raw_response=result_data.get("raw_response"),
                        original_result=result_data["result"],
                        reviewed_result=result_data["result"],
                        review_status=review_status,
                        confidence_score=final_score,
                        review_reason=conf_reason if review_status == ReviewStatus.PENDING_REVIEW else None,
                    )
                    item_repo.create(item)
                    success_count += 1

                except Exception as e:
                    failed_count += 1
                    print(f"保存第 {idx + 1} 个识别结果失败: {str(e)}")

            # 标记任务完成
            task_repo.mark_done(
                task_id,
                total_items=total_items,
                success_items=success_count,
                failed_items=failed_count,
            )

        except Exception as e:
            task_repo.mark_failed(task_id, str(e))
            raise

        finally:
            db.close()
