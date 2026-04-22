"""
智谱 GLM Chat Completions API 请求构建器

API 文档: https://open.bigmodel.cn/dev/api
端点: POST /api/paas/v4/chat/completions

智谱 API 兼容 OpenAI Chat Completions 格式：
- 图片通过 image_url 字段传递 base64 data URI
- 不支持 PDF 直传，需要先转图片
"""
import base64
from typing import Dict, Any
from .base import RequestBuilder
from app.services.ai.transport import TransportMode


class ZhipuChatCompletionsRequestBuilder(RequestBuilder):
    """智谱 GLM Chat Completions API 请求构建器"""

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
        """构建智谱 Chat Completions API 请求体"""

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
            raise NotImplementedError("智谱 API 不支持 PDF 直传，请使用 convert_to_images 策略")
        elif transport_mode == TransportMode.TEXT_ONLY:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]
        else:
            request["messages"] = [
                {"role": "user", "content": prompt}
            ]

        return request
