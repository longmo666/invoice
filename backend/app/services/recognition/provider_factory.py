"""
AI 提供商客户端工厂

根据 api_style 分流到不同的客户端实现：
- zhipu_ocr → ZhipuOCRClient（两步 OCR 流程，不走 builder/parser）
- 其他 → UnifiedAIClient（标准 builder/parser 多态体系）
"""
from typing import Optional
from app.services.recognition.provider_base import AIProviderClient
from app.services.recognition.unified_client import UnifiedAIClient
from app.services.recognition.zhipu_ocr_client import ZhipuOCRClient


class ProviderClientFactory:
    """AI 提供商客户端工厂"""

    @staticmethod
    def create_client(
        provider_vendor: str,
        api_style: str,
        base_url: str,
        api_key: str,
        model_name: str,
        timeout: int = 60,
        temperature: float = 0.1,
        max_tokens: int = 4000,
        ocr_chat_model: Optional[str] = None,
    ) -> AIProviderClient:
        """
        创建 AI 提供商客户端

        zhipu_ocr 走专用 OCR 客户端，其他走统一客户端。
        """
        if api_style == "zhipu_ocr":
            return ZhipuOCRClient(
                ocr_chat_model=ocr_chat_model,
                provider_vendor=provider_vendor,
                api_style=api_style,
                base_url=base_url,
                api_key=api_key,
                model_name=model_name,
                timeout=timeout,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        return UnifiedAIClient(
            provider_vendor=provider_vendor,
            api_style=api_style,
            base_url=base_url,
            api_key=api_key,
            model_name=model_name,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
        )
