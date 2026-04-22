from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.ai_config import AIConfig
from app.repositories.ai_config import AIConfigRepository
from app.schemas.ai_config import AIConfigCreate, AIConfigUpdate
from app.core.exceptions import ValidationException, NotFoundException
from app.services.recognition.provider_factory import ProviderClientFactory
from app.services.recognition.provider_base import TestConnectionResult
from app.utils import mask_api_key


class AIConfigService:
    """AI 配置服务"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AIConfigRepository(db)

    def create_config(self, data: AIConfigCreate) -> AIConfig:
        """
        创建 AI 配置

        Args:
            data: 配置数据

        Returns:
            创建的配置

        Raises:
            ValidationException: 配置名称已存在
        """
        # 检查名称是否已存在
        if self.repo.exists_by_name(data.name):
            raise ValidationException(f"配置名称 '{data.name}' 已存在")

        # 创建配置
        config = AIConfig(
            name=data.name,
            provider_vendor=data.provider_vendor.value,
            api_style=data.api_style.value,
            base_url=data.base_url,
            model_name=data.model_name,
            api_key=data.api_key,
            timeout=data.timeout,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            max_concurrency=data.max_concurrency,
            supports_image_input=data.supports_image_input,
            supports_pdf_file_input=data.supports_pdf_file_input,
            supports_file_id=data.supports_file_id,
            supports_file_url=data.supports_file_url,
            requires_files_api=data.requires_files_api,
            supports_structured_json=data.supports_structured_json,
            pdf_strategy=data.pdf_strategy.value,
            ocr_chat_model=data.ocr_chat_model,
            enabled=data.enabled,
            active=False
        )

        return self.repo.create(config)

    def update_config(self, config_id: int, data: AIConfigUpdate) -> AIConfig:
        """
        更新 AI 配置

        Args:
            config_id: 配置 ID
            data: 更新数据

        Returns:
            更新后的配置

        Raises:
            NotFoundException: 配置不存在
            ValidationException: 配置名称已存在
        """
        config = self.repo.get_by_id(config_id)
        if not config:
            raise NotFoundException("配置不存在")

        # 检查名称是否已存在（排除当前配置）
        if data.name and self.repo.exists_by_name(data.name, exclude_id=config_id):
            raise ValidationException(f"配置名称 '{data.name}' 已存在")

        # 更新字段
        if data.name is not None:
            config.name = data.name
        if data.provider_vendor is not None:
            config.provider_vendor = data.provider_vendor.value
        if data.api_style is not None:
            config.api_style = data.api_style.value
        if data.base_url is not None:
            config.base_url = data.base_url
        if data.model_name is not None:
            config.model_name = data.model_name
        if data.api_key is not None:
            config.api_key = data.api_key
        if data.timeout is not None:
            config.timeout = data.timeout
        if data.temperature is not None:
            config.temperature = data.temperature
        if data.max_tokens is not None:
            config.max_tokens = data.max_tokens
        if data.max_concurrency is not None:
            config.max_concurrency = data.max_concurrency
        if data.supports_image_input is not None:
            config.supports_image_input = data.supports_image_input
        if data.supports_pdf_file_input is not None:
            config.supports_pdf_file_input = data.supports_pdf_file_input
        if data.supports_file_id is not None:
            config.supports_file_id = data.supports_file_id
        if data.supports_file_url is not None:
            config.supports_file_url = data.supports_file_url
        if data.requires_files_api is not None:
            config.requires_files_api = data.requires_files_api
        if data.supports_structured_json is not None:
            config.supports_structured_json = data.supports_structured_json
        if data.pdf_strategy is not None:
            config.pdf_strategy = data.pdf_strategy.value
        if data.ocr_chat_model is not None:
            config.ocr_chat_model = data.ocr_chat_model
        if data.enabled is not None:
            config.enabled = data.enabled

        return self.repo.update(config)

    def delete_config(self, config_id: int) -> bool:
        """
        删除 AI 配置（物理删除）

        Args:
            config_id: 配置 ID

        Returns:
            是否成功

        Raises:
            ValidationException: 不能删除激活的配置
        """
        config = self.repo.get_by_id(config_id)
        if not config:
            return False

        if config.active:
            raise ValidationException("不能删除激活的配置，请先激活其他配置")

        # 物理删除
        self.db.delete(config)
        self.db.commit()
        return True

    def get_config(self, config_id: int) -> Optional[AIConfig]:
        """获取配置详情"""
        config = self.repo.get_by_id(config_id)
        if config:
            # 添加脱敏字段
            config.api_key_masked = mask_api_key(config.api_key)
            config.has_api_key = bool(config.api_key)
        return config

    def list_configs(self) -> List[AIConfig]:
        """获取所有配置（管理员列表）"""
        configs = self.repo.get_all()
        # 为每个配置添加脱敏字段
        for config in configs:
            config.api_key_masked = mask_api_key(config.api_key)
            config.has_api_key = bool(config.api_key)
        return configs

    def set_active(self, config_id: int) -> bool:
        """
        设置激活配置

        Args:
            config_id: 配置 ID

        Returns:
            是否成功

        Raises:
            NotFoundException: 配置不存在
            ValidationException: 配置未启用
        """
        config = self.repo.get_by_id(config_id)
        if not config:
            raise NotFoundException("配置不存在")

        if not config.enabled:
            raise ValidationException("不能激活已禁用的配置")

        return self.repo.set_active(config_id)

    def toggle_enabled(self, config_id: int, enabled: bool) -> bool:
        """
        切换启用状态

        Args:
            config_id: 配置 ID
            enabled: 是否启用

        Returns:
            是否成功

        Raises:
            NotFoundException: 配置不存在
            ValidationException: 不能禁用激活的配置
        """
        config = self.repo.get_by_id(config_id)
        if not config:
            raise NotFoundException("配置不存在")

        if not enabled and config.active:
            raise ValidationException("不能禁用激活的配置，请先激活其他配置")

        return self.repo.toggle_enabled(config_id, enabled)

    async def test_connection(
        self,
        provider_vendor: str,
        api_style: str,
        base_url: str,
        model_name: str,
        api_key: str,
        timeout: int = 60,
        ocr_chat_model: str = None
    ) -> TestConnectionResult:
        """
        测试 AI 配置连接

        Args:
            provider_vendor: 提供商厂商
            api_style: API 风格
            base_url: API 基础 URL
            model_name: 模型名称
            api_key: API 密钥
            timeout: 超时时间

        Returns:
            包含 success, message, latency_ms, request_path, status_code 的字典
        """
        try:
            client = ProviderClientFactory.create_client(
                provider_vendor=provider_vendor,
                api_style=api_style,
                base_url=base_url,
                api_key=api_key,
                model_name=model_name,
                timeout=timeout,
                ocr_chat_model=ocr_chat_model,
            )

            return await client.test_connection()

        except Exception as e:
            return {
                "success": False,
                "message": f"测试失败: {str(e)}",
                "latency_ms": None,
                "request_path": None,
                "status_code": None,
                "diagnostic_steps": [],
            }
