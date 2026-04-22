"""
Google Gemini generateContent API 响应解析器
"""
from typing import Dict, Any
from .base import ResponseParser, StandardResponse


class GeminiGenerateContentResponseParser(ResponseParser):
    """Google Gemini generateContent API 响应解析器"""

    def parse(self, response_data: Dict[str, Any]) -> StandardResponse:
        """解析 Gemini generateContent API 响应"""

        content = ""
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            candidate = response_data["candidates"][0]
            candidate_content = candidate.get("content", {})
            parts = candidate_content.get("parts", [])
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    content += part["text"]

        model = response_data.get("modelVersion", "unknown")

        usage_metadata = response_data.get("usageMetadata", {})
        usage = {
            "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
            "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
            "total_tokens": usage_metadata.get("totalTokenCount", 0),
        }

        finish_reason = None
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            finish_reason = response_data["candidates"][0].get("finishReason")

        return StandardResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=finish_reason
        )
