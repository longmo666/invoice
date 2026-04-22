"""
Anthropic Messages API 请求构建器
"""
import base64
from typing import Dict, Any
from .base import RequestBuilder
from app.services.ai.transport import TransportMode


class AnthropicMessagesRequestBuilder(RequestBuilder):
    """Anthropic Messages API 请求构建器"""

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
        """构建 Anthropic Messages API 请求体"""

        request = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if transport_mode == TransportMode.MULTIMODAL_IMAGE and image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            request["messages"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        elif transport_mode == TransportMode.DOCUMENT_FILE and file_data:
            pdf_base64 = base64.b64encode(file_data).decode('utf-8')
            request["messages"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        }
                    ]
                }
            ]
        elif transport_mode == TransportMode.TEXT_ONLY:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]
        else:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]

        return request
