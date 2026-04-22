"""
OpenAI Chat Completions API 请求构建器
"""
import base64
from typing import Dict, Any
from .base import RequestBuilder
from app.services.ai.transport import TransportMode


class OpenAIChatCompletionsRequestBuilder(RequestBuilder):
    """OpenAI Chat Completions API 请求构建器"""

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
        """构建 OpenAI Chat Completions API 请求体"""

        request = {
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if transport_mode == TransportMode.MULTIMODAL_IMAGE and image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            request["messages"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        elif transport_mode == TransportMode.DOCUMENT_FILE:
            raise NotImplementedError("当前 API 风格不支持 PDF 直传，请使用 convert_to_images 策略")
        elif transport_mode == TransportMode.TEXT_ONLY:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]
        elif file_id:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]
            request["file_ids"] = [file_id]
        elif file_url:
            request["messages"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": file_url}}
                    ]
                }
            ]
        else:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]

        return request
