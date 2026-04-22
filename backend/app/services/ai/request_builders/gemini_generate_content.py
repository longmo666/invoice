"""
Google Gemini generateContent API 请求构建器

API 文档: https://ai.google.dev/api/generate-content
端点: POST /v1beta/models/{model}:generateContent
"""
import base64
from typing import Dict, Any
from .base import RequestBuilder
from app.services.ai.transport import TransportMode


class GeminiGenerateContentRequestBuilder(RequestBuilder):
    """Google Gemini generateContent API 请求构建器"""

    def build_request(
        self,
        prompt: str,
        transport_mode: TransportMode,
        image_data: bytes = None,
        file_data: bytes = None,
        file_name: str = None,
        file_id: str = None,
        file_url: str = None,
        model_name: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """构建 Gemini generateContent API 请求体"""

        request = {
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if transport_mode == TransportMode.MULTIMODAL_IMAGE and image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            request["contents"] = [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        elif transport_mode == TransportMode.DOCUMENT_FILE and file_data:
            pdf_base64 = base64.b64encode(file_data).decode('utf-8')
            request["contents"] = [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "application/pdf",
                                "data": pdf_base64
                            }
                        }
                    ]
                }
            ]
        elif transport_mode == TransportMode.TEXT_ONLY:
            request["contents"] = [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        else:
            request["contents"] = [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]

        return request
