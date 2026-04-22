from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProviderVendorEnum(str, Enum):
    """AI 提供商厂商枚举"""
    OPENAI_COMPATIBLE = "openai_compatible"
    ANTHROPIC_COMPATIBLE = "anthropic_compatible"
    GOOGLE_COMPATIBLE = "google_compatible"
    ZHIPU_COMPATIBLE = "zhipu_compatible"


class APIStyleEnum(str, Enum):
    """API 风格枚举"""
    OPENAI_RESPONSES = "openai_responses"
    OPENAI_CHAT_COMPLETIONS = "openai_chat_completions"
    ANTHROPIC_MESSAGES = "anthropic_messages"
    GEMINI_GENERATE_CONTENT = "gemini_generate_content"
    ZHIPU_CHAT_COMPLETIONS = "zhipu_chat_completions"
    ZHIPU_OCR = "zhipu_ocr"


class PDFStrategyEnum(str, Enum):
    """PDF 处理策略枚举"""
    DIRECT_PDF = "direct_pdf"
    CONVERT_TO_IMAGES = "convert_to_images"


# ==================== 请求 Schema ====================

class AIConfigCreate(BaseModel):
    """创建 AI 配置请求"""
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    provider_vendor: ProviderVendorEnum = Field(..., description="提供商厂商")
    api_style: APIStyleEnum = Field(..., description="API 风格")
    base_url: str = Field(..., min_length=1, max_length=500, description="API 基础 URL")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    api_key: str = Field(..., min_length=1, description="API 密钥")
    timeout: int = Field(default=60, ge=10, le=300, description="超时时间（秒）")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=4000, ge=100, le=100000, description="最大 token 数")
    max_concurrency: int = Field(default=1, ge=1, le=100, description="最大并发数")

    # 提供商能力
    supports_image_input: bool = Field(default=True, description="是否支持图片输入")
    supports_pdf_file_input: bool = Field(default=False, description="是否支持 PDF 文件输入")
    supports_file_id: bool = Field(default=False, description="是否支持文件 ID")
    supports_file_url: bool = Field(default=False, description="是否支持文件 URL")
    requires_files_api: bool = Field(default=False, description="是否需要先调用 files API")
    supports_structured_json: bool = Field(default=False, description="是否支持结构化 JSON 输出")

    # PDF 处理策略
    pdf_strategy: PDFStrategyEnum = Field(default=PDFStrategyEnum.CONVERT_TO_IMAGES, description="PDF 处理策略")

    # 智谱 OCR 专用
    ocr_chat_model: Optional[str] = Field(None, max_length=100, description="OCR 模式下结构化提取用的 chat 模型")

    # 状态
    enabled: bool = Field(default=True, description="是否启用")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("配置名称不能为空")
        return v.strip()

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            raise ValueError("API 基础 URL 必须以 http:// 或 https:// 开头")
        return v.rstrip('/')


class AIConfigUpdate(BaseModel):
    """更新 AI 配置请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="配置名称")
    provider_vendor: Optional[ProviderVendorEnum] = Field(None, description="提供商厂商")
    api_style: Optional[APIStyleEnum] = Field(None, description="API 风格")
    base_url: Optional[str] = Field(None, min_length=1, max_length=500, description="API 基础 URL")
    model_name: Optional[str] = Field(None, min_length=1, max_length=100, description="模型名称")
    api_key: Optional[str] = Field(None, min_length=1, description="API 密钥")
    timeout: Optional[int] = Field(None, ge=10, le=300, description="超时时间（秒）")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=100, le=100000, description="最大 token 数")
    max_concurrency: Optional[int] = Field(None, ge=1, le=100, description="最大并发数")

    # 提供商能力
    supports_image_input: Optional[bool] = Field(None, description="是否支持图片输入")
    supports_pdf_file_input: Optional[bool] = Field(None, description="是否支持 PDF 文件输入")
    supports_file_id: Optional[bool] = Field(None, description="是否支持文件 ID")
    supports_file_url: Optional[bool] = Field(None, description="是否支持文件 URL")
    requires_files_api: Optional[bool] = Field(None, description="是否需要先调用 files API")
    supports_structured_json: Optional[bool] = Field(None, description="是否支持结构化 JSON 输出")

    # PDF 处理策略
    pdf_strategy: Optional[PDFStrategyEnum] = Field(None, description="PDF 处理策略")

    # 智谱 OCR 专用
    ocr_chat_model: Optional[str] = Field(None, max_length=100, description="OCR 模式下结构化提取用的 chat 模型")

    # 状态
    enabled: Optional[bool] = Field(None, description="是否启用")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("配置名称不能为空")
        return v.strip() if v else None

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v.startswith(('http://', 'https://')):
                raise ValueError("API 基础 URL 必须以 http:// 或 https:// 开头")
            return v.rstrip('/')
        return None


class AIConfigTestRequest(BaseModel):
    """测试 AI 配置请求（已废弃，改用 config_id）"""
    provider_vendor: ProviderVendorEnum = Field(..., description="提供商厂商")
    api_style: APIStyleEnum = Field(..., description="API 风格")
    base_url: str = Field(..., description="API 基础 URL")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field(..., description="API 密钥")
    timeout: int = Field(default=60, description="超时时间（秒）")


# ==================== 响应 Schema ====================

class AIConfigDetail(BaseModel):
    """AI 配置详情"""
    id: int
    name: str
    provider_vendor: ProviderVendorEnum
    api_style: APIStyleEnum
    base_url: str
    model_name: str
    api_key_masked: str  # 脱敏后的 API Key
    has_api_key: bool  # 是否已设置 API Key
    timeout: int
    temperature: float
    max_tokens: int
    max_concurrency: int
    supports_image_input: bool
    supports_pdf_file_input: bool
    supports_file_id: bool
    supports_file_url: bool
    requires_files_api: bool
    supports_structured_json: bool
    pdf_strategy: PDFStrategyEnum
    ocr_chat_model: Optional[str] = None
    enabled: bool
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIConfigListItem(BaseModel):
    """AI 配置列表项"""
    id: int
    name: str
    provider_vendor: ProviderVendorEnum
    api_style: APIStyleEnum
    base_url: str
    model_name: str
    api_key_masked: str  # 脱敏后的 API Key
    has_api_key: bool  # 是否已设置 API Key
    timeout: int
    temperature: float
    max_tokens: int
    max_concurrency: int
    supports_image_input: bool
    supports_pdf_file_input: bool
    supports_file_id: bool
    supports_file_url: bool
    requires_files_api: bool
    supports_structured_json: bool
    pdf_strategy: PDFStrategyEnum
    ocr_chat_model: Optional[str] = None
    enabled: bool
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiagnosticStep(BaseModel):
    """诊断步骤"""
    step: str
    url: str = ""
    status_code: Optional[int] = None
    latency_ms: Optional[int] = None
    success: bool = False
    detail: str = ""


class AIConfigTestResponse(BaseModel):
    """测试 AI 配置响应"""
    success: bool
    message: str
    latency_ms: Optional[int] = None
    request_path: Optional[str] = None
    status_code: Optional[int] = None
    diagnostic_steps: list[DiagnosticStep] = []

