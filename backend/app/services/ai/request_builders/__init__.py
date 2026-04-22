"""
请求构建器工厂

所有 API 风格的请求构建器统一注册在此。
这是 AI 基础设施的唯一真相源，业务层只能通过此入口获取构建器。
"""
from .base import RequestBuilder
from .openai_responses import OpenAIResponsesRequestBuilder
from .openai_chat_completions import OpenAIChatCompletionsRequestBuilder
from .anthropic_messages import AnthropicMessagesRequestBuilder
from .gemini_generate_content import GeminiGenerateContentRequestBuilder
from .zhipu_chat_completions import ZhipuChatCompletionsRequestBuilder

_BUILDERS = {
    "openai_responses": OpenAIResponsesRequestBuilder,
    "openai_chat_completions": OpenAIChatCompletionsRequestBuilder,
    "anthropic_messages": AnthropicMessagesRequestBuilder,
    "gemini_generate_content": GeminiGenerateContentRequestBuilder,
    "zhipu_chat_completions": ZhipuChatCompletionsRequestBuilder,
}


def get_request_builder(api_style: str) -> RequestBuilder:
    """
    根据 API 风格获取请求构建器

    Args:
        api_style: API 风格

    Returns:
        请求构建器实例
    """
    builder_cls = _BUILDERS.get(api_style)
    if not builder_cls:
        raise ValueError(f"不支持的 API 风格: {api_style}")
    return builder_cls()


__all__ = [
    "RequestBuilder",
    "OpenAIResponsesRequestBuilder",
    "OpenAIChatCompletionsRequestBuilder",
    "AnthropicMessagesRequestBuilder",
    "GeminiGenerateContentRequestBuilder",
    "ZhipuChatCompletionsRequestBuilder",
    "get_request_builder",
]
