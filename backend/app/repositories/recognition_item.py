from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc
from app.models.recognition_item import RecognitionItem, ReviewStatus
from app.repositories.base import BaseRepository


class RecognitionItemRepository(BaseRepository[RecognitionItem]):
    """识别结果项仓储"""

    def __init__(self, db: Session):
        super().__init__(RecognitionItem, db)

    def get_by_id(self, id: int) -> Optional[RecognitionItem]:
        """根据ID获取（覆盖基类方法，使用 deleted_at 而非 is_deleted）"""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first()

    def get_by_task(self, task_id: int) -> List[RecognitionItem]:
        """获取任务的所有识别结果项"""
        return self.db.query(self.model).filter(
            self.model.task_id == task_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.item_index).all()

    def get_pending_review_items(
        self,
        user_id: Optional[int] = None,
        invoice_type: Optional[str] = None,
        limit: int = 50
    ) -> List[RecognitionItem]:
        """获取待复核的识别结果项，可按 invoice_type 过滤"""
        from app.models.recognition_task import RecognitionTask, InvoiceType

        query = self.db.query(self.model).filter(
            self.model.review_status == ReviewStatus.PENDING_REVIEW,
            self.model.deleted_at.is_(None)
        )

        if user_id or invoice_type:
            query = query.join(RecognitionTask)
            if user_id:
                query = query.filter(RecognitionTask.user_id == user_id)
            if invoice_type:
                query = query.filter(RecognitionTask.invoice_type == InvoiceType(invoice_type))

        return query.options(selectinload(self.model.task)).order_by(desc(self.model.created_at)).limit(limit).all()

    def update_review(
        self,
        item_id: int,
        reviewed_result: dict,
        review_status: ReviewStatus,
        reviewed_by: int
    ) -> bool:
        """更新复核结果"""
        item = self.get_by_id(item_id)
        if not item:
            return False

        item.reviewed_result = reviewed_result
        item.review_status = review_status
        item.reviewed_by = reviewed_by

        from sqlalchemy.sql import func
        item.reviewed_at = func.now()

        self.db.commit()
        return True

    def batch_create(self, items: List[RecognitionItem]) -> List[RecognitionItem]:
        """批量创建识别结果项"""
        self.db.add_all(items)
        self.db.commit()
        for item in items:
            self.db.refresh(item)
        return items

    def get_reviewed_items_by_task(self, task_id: int) -> List[RecognitionItem]:
        """获取任务的已复核结果项（用于导出）"""
        return self.db.query(self.model).filter(
            self.model.task_id == task_id,
            self.model.review_status.in_([ReviewStatus.AUTO_PASSED, ReviewStatus.MANUAL_CONFIRMED]),
            self.model.deleted_at.is_(None)
        ).order_by(self.model.item_index).all()
