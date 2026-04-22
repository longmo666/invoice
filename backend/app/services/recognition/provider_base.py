from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from typing_extensions import TypedDict
from enum import Enum


class RecognitionError(Exception):
    """识别异常，携带已完成的 diagnostic_steps 供上层消费"""

    def __init__(self, message: str, diagnostic_steps: list = None):
        super().__init__(message)
        self.diagnostic_steps = diagnostic_steps or []


class DiagnosticStepDict(TypedDict, total=False):
    """诊断步骤字典（统一构造）"""
    step: str
    url: str
    status_code: Optional[int]
    latency_ms: Optional[int]
    success: bool
    detail: str


def make_diagnostic_step(
    step: str,
    url: str = "",
    status_code: Optional[int] = None,
    latency_ms: Optional[int] = None,
    success: bool = False,
    detail: str = "",
) -> DiagnosticStepDict:
    """构造标准诊断步骤 dict，避免散落手写"""
    return DiagnosticStepDict(
        step=step,
        url=url,
        status_code=status_code,
        latency_ms=latency_ms,
        success=success,
        detail=detail,
    )


class TestConnectionResult(TypedDict):
    """test_connection() 返回值契约"""
    success: bool
    message: str
    latency_ms: Optional[int]
    request_path: Optional[str]
    status_code: Optional[int]
    diagnostic_steps: List[DiagnosticStepDict]


class ProviderVendor(str, Enum):
    """AI 提供商厂商"""
    OPENAI_COMPATIBLE = "openai_compatible"
    ANTHROPIC_COMPATIBLE = "anthropic_compatible"
    GOOGLE_COMPATIBLE = "google_compatible"
    ZHIPU_COMPATIBLE = "zhipu_compatible"


class APIStyle(str, Enum):
    """API 风格"""
    OPENAI_RESPONSES = "openai_responses"
    OPENAI_CHAT_COMPLETIONS = "openai_chat_completions"
    ANTHROPIC_MESSAGES = "anthropic_messages"
    GEMINI_GENERATE_CONTENT = "gemini_generate_content"
    ZHIPU_CHAT_COMPLETIONS = "zhipu_chat_completions"
    ZHIPU_OCR = "zhipu_ocr"


class AIProviderClient(ABC):
    """AI 提供商客户端抽象基类"""

    def __init__(
        self,
        provider_vendor: str,
        api_style: str,
        base_url: str,
        api_key: str,
        model_name: str,
        timeout: int = 60,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ):
        self.provider_vendor = provider_vendor
        self.api_style = api_style
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def recognize_invoice(
        self,
        image_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        识别发票（图片）

        Args:
            image_data: 图片二进制数据
            invoice_type: 发票类型 (vat_special, vat_normal, railway_ticket)
            prompt_template: 提示词模板

        Returns:
            识别结果字典
        """
        pass

    @abstractmethod
    async def recognize_invoice_from_pdf(
        self,
        pdf_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        识别发票（PDF 直传）

        Args:
            pdf_data: PDF 二进制数据
            invoice_type: 发票类型 (vat_special, vat_normal, railway_ticket)
            prompt_template: 提示词模板

        Returns:
            识别结果字典

        Raises:
            NotImplementedError: 当前 API 风格不支持 PDF 直传
        """
        pass

    @abstractmethod
    async def test_connection(self) -> TestConnectionResult:
        """
        测试连接

        Returns:
TestConnectionResult with keys: success, message, latency_ms, request_path, status_code, diagnostic_steps
        """
        pass
