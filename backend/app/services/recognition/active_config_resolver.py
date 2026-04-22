"""
激活配置解析器

负责获取和管理当前激活的 AI 配置
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.ai_config import AIConfig
from app.repositories.ai_config import AIConfigRepository


class ActiveConfigResolver:
    """激活配置解析器"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AIConfigRepository(db)

    def get_active_config(self) -> Optional[AIConfig]:
        """
        获取当前激活的 AI 配置

        Returns:
            激活的配置，如果没有则返回 None
        """
        return self.repo.get_active()

    def validate_active_config(self) -> AIConfig:
        """
        验证并获取激活配置

        Returns:
            激活的配置

        Raises:
            ValueError: 没有激活的配置
        """
        config = self.get_active_config()
        if not config:
            raise ValueError("未找到激活的 AI 配置，请先在管理员页面配置并激活 AI")
        return config

    def get_config_capability(self, config: AIConfig) -> dict:
        """
        获取配置的能力信息

        Args:
            config: AI 配置

        Returns:
            能力字典
        """
        return {
            "supports_image_input": config.supports_image_input,
            "supports_pdf_file_input": config.supports_pdf_file_input,
            "supports_file_id": config.supports_file_id,
            "supports_file_url": config.supports_file_url,
            "requires_files_api": config.requires_files_api,
            "supports_structured_json": config.supports_structured_json,
            "max_concurrency": config.max_concurrency
        }
