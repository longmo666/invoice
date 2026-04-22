from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from app.models.recognition_task import RecognitionTask, TaskStatus, InvoiceType
from app.repositories.base import BaseRepository


class RecognitionTaskRepository(BaseRepository[RecognitionTask]):
    """识别任务仓储"""

    def __init__(self, db: Session):
        super().__init__(RecognitionTask, db)

    def get_by_id(self, id: int) -> Optional[RecognitionTask]:
        """根据ID获取（覆盖基类方法，使用 deleted_at 而非 is_deleted）"""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first()

    def get_by_user(
        self,
        user_id: int,
        invoice_type: Optional[InvoiceType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[RecognitionTask]:
        """获取用户的识别任务列表"""
        query = self.db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.deleted_at.is_(None)
        )

        if invoice_type:
            query = query.filter(self.model.invoice_type == invoice_type)

        if status:
            query = query.filter(self.model.status == status)

        return query.order_by(desc(self.model.created_at)).limit(limit).all()

    def get_pending_tasks(self, limit: int = 10) -> List[RecognitionTask]:
        """获取待处理的任务（用于后台处理）"""
        return self.db.query(self.model).filter(
            self.model.status.in_([TaskStatus.UPLOADING, TaskStatus.PROCESSING]),
            self.model.deleted_at.is_(None)
        ).order_by(self.model.created_at).limit(limit).all()

    def update_progress(self, task_id: int, progress: int, status: Optional[TaskStatus] = None) -> bool:
        """更新任务进度"""
        task = self.get_by_id(task_id)
        if not task:
            return False

        task.progress = progress
        if status:
            task.status = status

        self.db.commit()
        return True

    def mark_failed(self, task_id: int, error_message: str) -> bool:
        """标记任务失败"""
        task = self.get_by_id(task_id)
        if not task:
            return False

        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.progress = 100

        self.db.commit()
        return True

    def mark_done(self, task_id: int, total_items: int, success_items: int, failed_items: int) -> bool:
        """标记任务完成"""
        task = self.get_by_id(task_id)
        if not task:
            return False

        task.status = TaskStatus.DONE
        task.progress = 100
        task.total_items = total_items
        task.success_items = success_items
        task.failed_items = failed_items

        from sqlalchemy.sql import func
        task.finished_at = func.now()

        self.db.commit()
        return True

    def get_paginated(
        self,
        user_id: int,
        invoice_type: Optional[InvoiceType] = None,
        status: Optional[TaskStatus] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[RecognitionTask], int]:
        """
        分页获取任务列表（带筛选）

        Returns:
            (任务列表, 总数)
        """
        query = self.db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.deleted_at.is_(None)
        )

        if invoice_type:
            query = query.filter(self.model.invoice_type == invoice_type)
        if status:
            query = query.filter(self.model.status == status)
        if keyword:
            query = query.filter(self.model.original_filename.ilike(f"%{keyword}%"))

        total = query.count()
        tasks = query.options(selectinload(self.model.items)) \
            .order_by(desc(self.model.created_at)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return tasks, total

    def get_admin_paginated(
        self,
        tab: str,
        invoice_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[dict], int]:
        """
        管理端分页获取任务列表（含用户名，eager load items）

        tab 决定基础过滤：
          - invoice → vat_special / vat_normal
          - train   → railway_ticket

        Returns:
            ([{task, username}, ...], total)
        """
        from app.models.user import User

        query = (
            self.db.query(self.model, User.username)
            .join(User, User.id == self.model.user_id)
            .filter(self.model.deleted_at.is_(None))
        )

        # tab 基础过滤
        if tab == "train":
            query = query.filter(self.model.invoice_type == InvoiceType.RAILWAY_TICKET)
        else:
            query = query.filter(
                self.model.invoice_type.in_([InvoiceType.VAT_SPECIAL, InvoiceType.VAT_NORMAL])
            )

        # 可选叠加过滤
        if invoice_type:
            query = query.filter(self.model.invoice_type == InvoiceType(invoice_type))
        if status:
            query = query.filter(self.model.status == TaskStatus(status))
        if keyword:
            query = query.filter(self.model.original_filename.ilike(f"%{keyword}%"))

        total = query.count()

        rows = (
            query
            .options(selectinload(self.model.items))
            .order_by(desc(self.model.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        result = [{"task": task, "username": username} for task, username in rows]
        return result, total
