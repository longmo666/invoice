"""
OpenAI Responses API 响应解析器
"""
from typing import Dict, Any
from .base import ResponseParser, StandardResponse


class OpenAIResponsesResponseParser(ResponseParser):
    """OpenAI Responses API 响应解析器"""

    def parse(self, response_data: Dict[str, Any]) -> StandardResponse:
        """解析 OpenAI Responses API 响应"""

        content = ""
        if "output" in response_data:
            output = response_data["output"]
            if isinstance(output, str):
                content = output
            elif isinstance(output, list):
                for item in output:
                    if isinstance(item, dict) and item.get("type") == "text":
                        content += item.get("text", "")
            elif isinstance(output, dict):
                content = output.get("text", "")

        model = response_data.get("model", "unknown")

        usage = response_data.get("usage", {})
        if not isinstance(usage, dict):
            usage = {}

        finish_reason = response_data.get("finish_reason")

        return StandardResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=finish_reason
        )
