"""
响应解析器工厂

所有 API 风格的响应解析器统一注册在此。
这是 AI 基础设施的唯一真相源，业务层只能通过此入口获取解析器。
"""
from .base import ResponseParser, StandardResponse
from .openai_responses import OpenAIResponsesResponseParser
from .openai_chat_completions import OpenAIChatCompletionsResponseParser
from .anthropic_messages import AnthropicMessagesResponseParser
from .gemini_generate_content import GeminiGenerateContentResponseParser
from .zhipu_chat_completions import ZhipuChatCompletionsResponseParser

_PARSERS = {
    "openai_responses": OpenAIResponsesResponseParser,
    "openai_chat_completions": OpenAIChatCompletionsResponseParser,
    "anthropic_messages": AnthropicMessagesResponseParser,
    "gemini_generate_content": GeminiGenerateContentResponseParser,
    "zhipu_chat_completions": ZhipuChatCompletionsResponseParser,
}


def get_response_parser(api_style: str) -> ResponseParser:
    """
    根据 API 风格获取响应解析器

    Args:
        api_style: API 风格

    Returns:
        响应解析器实例
    """
    parser_cls = _PARSERS.get(api_style)
    if not parser_cls:
        raise ValueError(f"不支持的 API 风格: {api_style}")
    return parser_cls()


__all__ = [
    "ResponseParser",
    "StandardResponse",
    "OpenAIResponsesResponseParser",
    "OpenAIChatCompletionsResponseParser",
    "AnthropicMessagesResponseParser",
    "GeminiGenerateContentResponseParser",
    "ZhipuChatCompletionsResponseParser",
    "get_response_parser",
]
