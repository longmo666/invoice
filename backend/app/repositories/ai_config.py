from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ai_config import AIConfig
from app.repositories.base import BaseRepository


class AIConfigRepository(BaseRepository[AIConfig]):
    """AI 配置仓储"""

    def __init__(self, db: Session):
        super().__init__(AIConfig, db)

    def get_by_id(self, id: int) -> Optional[AIConfig]:
        """根据ID获取（覆盖基类方法，使用 deleted_at 而非 is_deleted）"""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first()

    def get_active(self) -> Optional[AIConfig]:
        """获取当前激活的 AI 配置"""
        return self.db.query(self.model).filter(
            self.model.active == True,
            self.model.enabled == True,
            self.model.deleted_at.is_(None)
        ).first()

    def get_all_enabled(self) -> List[AIConfig]:
        """获取所有启用的配置（运行时使用）"""
        return self.db.query(self.model).filter(
            self.model.enabled == True,
            self.model.deleted_at.is_(None)
        ).order_by(desc(self.model.created_at)).all()

    def get_all(self) -> List[AIConfig]:
        """获取所有配置（管理员列表使用）"""
        return self.db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).order_by(desc(self.model.created_at)).all()

    def set_active(self, config_id: int) -> bool:
        """设置激活配置（同时取消其他配置的激活状态）"""
        # 先取消所有配置的激活状态
        self.db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).update({"active": False})

        # 激活指定配置
        config = self.get_by_id(config_id)
        if not config or not config.enabled:
            self.db.rollback()
            return False

        config.active = True
        self.db.commit()
        return True

    def toggle_enabled(self, config_id: int, enabled: bool) -> bool:
        """切换启用状态"""
        config = self.get_by_id(config_id)
        if not config:
            return False

        config.enabled = enabled
        # 如果禁用了激活的配置，同时取消激活状态
        if not enabled and config.active:
            config.active = False

        self.db.commit()
        return True

    def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """检查配置名称是否已存在"""
        query = self.db.query(self.model).filter(
            self.model.name == name,
            self.model.deleted_at.is_(None)
        )

        if exclude_id:
            query = query.filter(self.model.id != exclude_id)

        return query.first() is not None
