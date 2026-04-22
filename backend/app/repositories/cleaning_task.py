from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.cleaning_task import CleaningTask, CleaningStatus
from app.repositories.base import BaseRepository


class CleaningTaskRepository(BaseRepository[CleaningTask]):
    """文件清洗任务仓储"""

    def __init__(self, db: Session):
        super().__init__(CleaningTask, db)

    def get_by_user(self, user_id: int, status: Optional[CleaningStatus] = None) -> List[CleaningTask]:
        """获取用户的任务列表"""
        query = self.db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False
        )
        if status:
            query = query.filter(self.model.status == status)
        return query.order_by(self.model.created_at.desc()).all()

    def get_all_tasks(self, status: Optional[CleaningStatus] = None) -> List[CleaningTask]:
        """获取所有任务（管理员用）"""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)
        if status:
            query = query.filter(self.model.status == status)
        return query.order_by(self.model.created_at.desc()).all()

    def get_by_id_and_user(self, task_id: int, user_id: int) -> Optional[CleaningTask]:
        """获取用户的特定任务"""
        return self.db.query(self.model).filter(
            self.model.id == task_id,
            self.model.user_id == user_id,
            self.model.is_deleted == False
        ).first()
