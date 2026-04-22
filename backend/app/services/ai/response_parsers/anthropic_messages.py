"""
Anthropic Messages API 响应解析器
"""
from typing import Dict, Any
from .base import ResponseParser, StandardResponse


class AnthropicMessagesResponseParser(ResponseParser):
    """Anthropic Messages API 响应解析器"""

    def parse(self, response_data: Dict[str, Any]) -> StandardResponse:
        """解析 Anthropic Messages API 响应"""

        content = ""
        if "content" in response_data:
            content_data = response_data["content"]
            if isinstance(content_data, list):
                for block in content_data:
                    if isinstance(block, dict) and block.get("type") == "text":
                        content += block.get("text", "")
            elif isinstance(content_data, str):
                content = content_data

        model = response_data.get("model", "unknown")

        usage = response_data.get("usage", {})
        if not isinstance(usage, dict):
            usage = {}

        finish_reason = response_data.get("stop_reason")

        return StandardResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=finish_reason
        )
