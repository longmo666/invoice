"""
OpenAI Responses API 请求构建器
"""
import base64
from typing import Dict, Any
from .base import RequestBuilder


class OpenAIResponsesRequestBuilder(RequestBuilder):
    """OpenAI Responses API 请求构建器"""

    def build_request(
        self,
        prompt: str,
        transport_mode: str,
        image_data: bytes = None,
        pdf_data: bytes = None,
        file_id: str = None,
        file_url: str = None,
        model_name: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """构建 OpenAI Responses API 请求体"""

        request = {
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if transport_mode == "multimodal_image" and image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            request["input"] = [
                {"type": "text", "text": prompt},
                {"type": "image", "image": f"data:image/jpeg;base64,{image_base64}"}
            ]
        elif transport_mode == "multimodal_pdf" and pdf_data:
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            request["input"] = [
                {"type": "text", "text": prompt},
                {"type": "document", "document": f"data:application/pdf;base64,{pdf_base64}"}
            ]
        elif transport_mode == "file_id" and file_id:
            request["input"] = [
                {"type": "text", "text": prompt},
                {"type": "file", "file_id": file_id}
            ]
        elif transport_mode == "file_url" and file_url:
            request["input"] = [
                {"type": "text", "text": prompt},
                {"type": "file", "file_url": file_url}
            ]
        else:
            request["input"] = prompt

        return request
