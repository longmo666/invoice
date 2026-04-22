from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import Base


class AIConfig(Base):
    """AI 配置模型"""
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="配置名称")

    # 提供商配置（三层模型）
    provider_vendor = Column(String(50), nullable=False, comment="提供商厂商: openai_compatible, anthropic_compatible")
    api_style = Column(String(50), nullable=False, comment="API 风格: openai_responses, openai_chat_completions, anthropic_messages")
    base_url = Column(String(500), nullable=False, comment="API 基础 URL")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    api_key = Column(Text, nullable=False, comment="API 密钥")

    # 可选配置
    timeout = Column(Integer, default=60, comment="超时时间（秒）")
    temperature = Column(Float, default=0.1, comment="温度参数")
    max_tokens = Column(Integer, default=4000, comment="最大 token 数")
    max_concurrency = Column(Integer, default=1, nullable=False, comment="最大并发数（1 表示串行）")

    # 提供商能力
    supports_image_input = Column(Boolean, default=True, nullable=False, comment="是否支持图片输入")
    supports_pdf_file_input = Column(Boolean, default=False, nullable=False, comment="是否支持 PDF 文件输入")
    supports_file_id = Column(Boolean, default=False, nullable=False, comment="是否支持文件 ID")
    supports_file_url = Column(Boolean, default=False, nullable=False, comment="是否支持文件 URL")
    requires_files_api = Column(Boolean, default=False, nullable=False, comment="是否需要先调用 files API")
    supports_structured_json = Column(Boolean, default=False, nullable=False, comment="是否支持结构化 JSON 输出")

    # PDF 处理策略
    pdf_strategy = Column(String(50), default="convert_to_images", nullable=False, comment="PDF 处理策略: direct_pdf, convert_to_images")

    # 智谱 OCR 专用：结构化提取用的 chat 模型（OCR 模型不支持 chat，需要另一个模型做结构化）
    ocr_chat_model = Column(String(100), nullable=True, comment="OCR 模式下结构化提取用的 chat 模型")

    # 状态
    enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    active = Column(Boolean, default=False, nullable=False, comment="是否激活（只能有一个激活）")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="软删除时间")
