"""
AI HTTP 辅助函数

提供 API 端点路径、认证请求头、完整 URL 构造等公共纯函数。
所有需要构造 AI 请求 URL/Header 的模块统一使用此文件。
"""
from typing import Dict


def get_api_endpoint(api_style: str, model_name: str = "") -> str:
    """根据 API 风格返回端点路径"""
    endpoints = {
        "openai_responses": "/v1/responses",
        "openai_chat_completions": "/v1/chat/completions",
        "anthropic_messages": "/v1/messages",
        "gemini_generate_content": f"/v1beta/models/{model_name}:generateContent",
        "zhipu_chat_completions": "/api/paas/v4/chat/completions",
    }
    endpoint = endpoints.get(api_style)
    if not endpoint:
        raise ValueError(f"不支持的 API 风格: {api_style}")
    return endpoint


def build_auth_headers(provider_vendor: str, api_key: str) -> Dict[str, str]:
    """根据厂商类型构造认证请求头"""
    if provider_vendor == "openai_compatible":
        return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    elif provider_vendor == "anthropic_compatible":
        return {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    elif provider_vendor == "google_compatible":
        return {"Content-Type": "application/json"}
    elif provider_vendor == "zhipu_compatible":
        return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    else:
        raise ValueError(f"不支持的提供商厂商: {provider_vendor}")


def build_full_url(base_url: str, api_style: str, model_name: str, provider_vendor: str, api_key: str) -> str:
    """构造完整请求 URL"""
    url = f"{base_url}{get_api_endpoint(api_style, model_name)}"
    if provider_vendor == "google_compatible":
        url += f"?key={api_key}"
    return url
