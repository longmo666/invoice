from pathlib import Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.recognition_task import RecognitionTask, TaskStatus, InvoiceType, FileType, RecognitionMode
from app.models.recognition_item import RecognitionItem, ReviewStatus
from app.repositories.recognition_task import RecognitionTaskRepository
from app.repositories.recognition_item import RecognitionItemRepository
from app.repositories.ai_config import AIConfigRepository
from app.core.exceptions import ValidationException
from app.core.config import settings
from app.services.task_processor import TaskProcessor

# 存储路径
UPLOAD_DIR = Path(settings.STORAGE_BASE_DIR) / "recognition" / "uploads"
RESULT_DIR = Path(settings.STORAGE_BASE_DIR) / "recognition" / "results"

# 限制配置
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | {'.pdf', '.xml', '.ofd'}


class RecognitionService:
    """识别服务"""

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = RecognitionTaskRepository(db)
        self.item_repo = RecognitionItemRepository(db)
        self.ai_config_repo = AIConfigRepository(db)
        self._ensure_directories()

    def _ensure_directories(self):
        """确保存储目录存在"""
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        RESULT_DIR.mkdir(parents=True, exist_ok=True)

    def _detect_file_type(self, filename: str) -> FileType:
        """检测文件类型"""
        ext = Path(filename).suffix.lower()
        if ext in SUPPORTED_IMAGE_EXTENSIONS:
            return FileType.IMAGE
        elif ext == '.pdf':
            return FileType.PDF
        elif ext == '.xml':
            return FileType.XML
        elif ext == '.ofd':
            return FileType.OFD
        else:
            raise ValidationException(f"不支持的文件类型: {ext}")

    async def create_task(
        self,
        user_id: int,
        file: UploadFile,
        invoice_type: InvoiceType,
        recognition_mode: RecognitionMode = RecognitionMode.AI
    ) -> RecognitionTask:
        """
        创建识别任务

        Args:
            user_id: 用户 ID
            file: 上传的文件
            invoice_type: 发票类型
            recognition_mode: 识别模式

        Returns:
            创建的任务
        """
        # 验证文件
        if not file.filename:
            raise ValidationException("文件名不能为空")

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            raise ValidationException(f"不支持的文件格式: {file_ext}")

        # 检测文件类型
        file_type = self._detect_file_type(file.filename)

        # 保存上传文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{user_id}_{file.filename}"
        upload_path = UPLOAD_DIR / safe_filename

        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise ValidationException(f"文件大小超过限制 ({MAX_UPLOAD_SIZE / 1024 / 1024}MB)")

        with open(upload_path, "wb") as f:
            f.write(content)

        # 获取激活的 AI 配置
        ai_config = self.ai_config_repo.get_active()
        if recognition_mode == RecognitionMode.AI and not ai_config:
            raise ValidationException("未找到激活的 AI 配置，请先在管理员页面配置 AI")

        # 创建任务
        task = RecognitionTask(
            user_id=user_id,
            original_filename=file.filename,
            file_type=file_type,
            file_path=str(upload_path),
            file_size=len(content),
            invoice_type=invoice_type,
            recognition_mode=recognition_mode,
            ai_config_id=ai_config.id if ai_config else None,
            status=TaskStatus.UPLOADING,
            progress=5
        )
        task = self.task_repo.create(task)

        # 启动后台处理
        TaskProcessor.start_processing(task.id, upload_path)

        return task

    def get_task(self, task_id: int, user_id: int) -> Optional[RecognitionTask]:
        """获取任务详情"""
        task = self.task_repo.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return None
        return task

    def list_tasks(
        self,
        user_id: int,
        invoice_type: Optional[InvoiceType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[RecognitionTask]:
        """获取任务列表"""
        return self.task_repo.get_by_user(user_id, invoice_type, status, limit)

    def list_tasks_paginated(
        self,
        user_id: int,
        invoice_type: Optional[InvoiceType] = None,
        status: Optional[TaskStatus] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """分页获取任务列表，服务端聚合摘要（避免 N+1）"""
        tasks, total = self.task_repo.get_paginated(
            user_id, invoice_type, status, keyword, page, page_size
        )

        items = []
        for task in tasks:
            # 从 task.items 取最佳结果的摘要，避免前端逐条请求详情
            best_item = self._get_best_item(task)
            summary = {}
            confidence_score = None
            review_status = None
            if best_item:
                summary = best_item.reviewed_result or best_item.original_result or {}
                confidence_score = float(best_item.confidence_score) if best_item.confidence_score else None
                review_status = best_item.review_status.value if best_item.review_status else None

            items.append({
                "id": task.id,
                "original_filename": task.original_filename,
                "file_type": task.file_type.value if task.file_type else None,
                "invoice_type": task.invoice_type.value if task.invoice_type else None,
                "status": task.status.value if task.status else None,
                "progress": task.progress,
                "total_items": task.total_items,
                "success_items": task.success_items,
                "failed_items": task.failed_items,
                "error_message": task.error_message,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "finished_at": task.finished_at.isoformat() if task.finished_at else None,
                "confidence_score": confidence_score,
                "review_status": review_status,
                "summary": summary,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def _get_best_item(self, task: RecognitionTask):
        """从任务的 items 中取最佳结果项（已复核 > 自动通过 > 最高置信度）"""
        if not task.items:
            return None
        from app.models.recognition_item import ReviewStatus
        for rs in [ReviewStatus.MANUAL_CONFIRMED, ReviewStatus.AUTO_PASSED]:
            for item in task.items:
                if item.review_status == rs and item.deleted_at is None:
                    return item
        # 按置信度降序
        valid = [i for i in task.items if i.deleted_at is None]
        if not valid:
            return None
        return max(valid, key=lambda i: float(i.confidence_score or 0))

    def batch_delete_tasks(self, task_ids: List[int], user_id: int) -> int:
        """批量物理删除任务（用户只能删自己的）"""
        deleted = 0
        for tid in task_ids:
            if self.delete_task(tid, user_id):
                deleted += 1
        return deleted

    def get_pending_review_items(self, user_id: int, invoice_type: str = None, limit: int = 50) -> List[RecognitionItem]:
        """获取待复核的识别结果项，可按 invoice_type 过滤"""
        return self.item_repo.get_pending_review_items(user_id, invoice_type=invoice_type, limit=limit)

    def update_review(
        self,
        item_id: int,
        user_id: int,
        reviewed_result: dict,
        review_status: ReviewStatus
    ) -> bool:
        """更新复核结果"""
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return False

        # 验证权限
        task = self.task_repo.get_by_id(item.task_id)
        if not task or task.user_id != user_id:
            return False

        return self.item_repo.update_review(item_id, reviewed_result, review_status, user_id)

    def void_item(self, item_id: int, user_id: int) -> bool:
        """作废识别结果项（物理删除）"""
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return False

        # 验证权限
        task = self.task_repo.get_by_id(item.task_id)
        if not task or task.user_id != user_id:
            return False

        try:
            self.db.delete(item)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Void item {item_id} failed: {e}")
            return False

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """物理删除任务及其关联数据和文件"""
        task = self.task_repo.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return False
        return self._hard_delete_task(task)

    def admin_delete_tasks(self, task_ids: List[int]) -> int:
        """管理员批量物理删除任务"""
        deleted = 0
        for tid in task_ids:
            task = self.db.query(RecognitionTask).filter(RecognitionTask.id == tid).first()
            if task and self._hard_delete_task(task):
                deleted += 1
        return deleted

    def _hard_delete_task(self, task: RecognitionTask) -> bool:
        """物理删除单个任务：删除文件 + 删除 items + 删除 task"""
        try:
            # 删除上传文件
            if task.file_path:
                fp = Path(task.file_path)
                if fp.exists():
                    fp.unlink()
            # 删除 items
            self.db.query(RecognitionItem).filter(RecognitionItem.task_id == task.id).delete()
            # 删除 task
            self.db.delete(task)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Delete task {task.id} failed: {e}")
            return False

    def admin_list_tasks(
        self,
        invoice_type: Optional[InvoiceType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 200
    ) -> List[RecognitionTask]:
        """管理员获取所有用户的任务列表"""
        query = self.db.query(RecognitionTask)
        if invoice_type:
            query = query.filter(RecognitionTask.invoice_type == invoice_type)
        if status:
            query = query.filter(RecognitionTask.status == status)
        return query.order_by(RecognitionTask.created_at.desc()).limit(limit).all()

    def admin_list_tasks_with_user(
        self,
        invoice_type: Optional[InvoiceType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 200
    ) -> List[dict]:
        """管理员获取所有用户的任务列表（含用户名）"""
        from app.repositories.user import UserRepository
        from app.schemas.recognition import RecognitionTaskListItem

        tasks = self.admin_list_tasks(invoice_type, status, limit)
        user_repo = UserRepository(self.db)

        # 缓存用户名避免重复查询
        user_cache: dict = {}
        task_list = []
        for t in tasks:
            d = RecognitionTaskListItem.model_validate(t).model_dump()
            d["user_id"] = t.user_id
            if t.user_id not in user_cache:
                user = user_repo.get_by_id(t.user_id)
                user_cache[t.user_id] = user.username if user else str(t.user_id)
            d["username"] = user_cache[t.user_id]
            d["recognition_mode"] = t.recognition_mode.value
            d["error_message"] = t.error_message
            task_list.append(d)

        return task_list

    def admin_get_task(self, task_id: int) -> Optional[RecognitionTask]:
        """管理员获取任务详情（不限用户）"""
        return self.db.query(RecognitionTask).filter(RecognitionTask.id == task_id).first()

    def admin_list_tasks_paginated(
        self,
        tab: str,
        invoice_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """管理端分页获取任务列表，服务端聚合摘要 + 可抵扣税额（消除 N+1）"""
        from app.services.recognition.deductible_tax import calculate_deductible_tax

        rows, total = self.task_repo.get_admin_paginated(
            tab=tab,
            invoice_type=invoice_type,
            status=status,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )

        items = []
        for row in rows:
            task = row["task"]
            username = row["username"]

            best_item = self._get_best_item(task)
            result_data = {}
            confidence_score = None
            if best_item:
                result_data = best_item.reviewed_result or best_item.original_result or {}
                confidence_score = float(best_item.confidence_score) if best_item.confidence_score else None

            inv_type = task.invoice_type.value if task.invoice_type else ""
            deductible = calculate_deductible_tax(result_data, inv_type)
            deductible_str = f"{deductible:.2f}" if deductible > 0 else ""

            summary = {
                "invoice_number": result_data.get("invoice_number", ""),
                "invoice_date": result_data.get("invoice_date", ""),
                "buyer_name": result_data.get("buyer_name", ""),
                "seller_name": result_data.get("seller_name", ""),
                "total_amount": result_data.get("total_amount", ""),
                "train_number": result_data.get("train_number", ""),
                "departure_station": result_data.get("departure_station", ""),
                "train_date": result_data.get("train_date", result_data.get("invoice_date", "")),
                "ticket_price": result_data.get("ticket_price", ""),
                "passenger_name": result_data.get("passenger_name", ""),
                "ticket_id": result_data.get("ticket_id", result_data.get("invoice_number", "")),
                "seat_class": result_data.get("seat_class", ""),
                "deductible_tax": deductible_str,
            }

            items.append({
                "id": task.id,
                "user_id": task.user_id,
                "username": username,
                "original_filename": task.original_filename,
                "invoice_type": inv_type,
                "status": task.status.value if task.status else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "confidence_score": confidence_score,
                "error_message": task.error_message,
                "summary": summary,
            })

        import math
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
