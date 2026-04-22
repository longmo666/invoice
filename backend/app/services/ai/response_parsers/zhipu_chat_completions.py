"""
智谱 GLM Chat Completions API 响应解析器
"""
from typing import Dict, Any
from .base import ResponseParser, StandardResponse


class ZhipuChatCompletionsResponseParser(ResponseParser):
    """智谱 GLM Chat Completions API 响应解析器"""

    def parse(self, response_data: Dict[str, Any]) -> StandardResponse:
        """解析智谱 Chat Completions API 响应"""

        content = ""
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice:
                message = choice["message"]
                if isinstance(message, dict):
                    content = message.get("content", "")
                elif isinstance(message, str):
                    content = message

        model = response_data.get("model", "unknown")

        usage = response_data.get("usage", {})
        if not isinstance(usage, dict):
            usage = {}

        finish_reason = None
        if "choices" in response_data and len(response_data["choices"]) > 0:
            finish_reason = response_data["choices"][0].get("finish_reason")

        return StandardResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=finish_reason
        )
