from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.user import User, UserStatus, UserRole


class UserRepository(BaseRepository[User]):
    """用户仓储"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取"""
        return self.db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()

    def update_last_login(self, user_id: int) -> None:
        """更新最后登录时间"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            self.db.commit()

    def batch_delete(self, ids: List[int]) -> int:
        """批量软删除"""
        count = self.db.query(User).filter(
            User.id.in_(ids),
            User.is_deleted == False
        ).update({"is_deleted": True}, synchronize_session=False)
        self.db.commit()
        return count

    def update_status(self, user_id: int, status: UserStatus) -> Optional[User]:
        """更新用户状态"""
        user = self.get_by_id(user_id)
        if user:
            user.status = status
            self.db.commit()
            self.db.refresh(user)
        return user

    def add_quota(self, user_id: int, amount: int) -> Optional[User]:
        """增加额度"""
        user = self.get_by_id(user_id)
        if user:
            user.remaining_quota += amount
            self.db.commit()
            self.db.refresh(user)
        return user

    def count_by_role(self, role: UserRole) -> int:
        """统计指定角色的用户数量"""
        return self.db.query(func.count(User.id)).filter(
            User.role == role,
            User.is_deleted == False
        ).scalar() or 0
