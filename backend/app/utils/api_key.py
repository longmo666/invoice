"""API Key 工具函数"""


def mask_api_key(api_key: str) -> str:
    """
    脱敏 API Key

    Args:
        api_key: 原始 API Key

    Returns:
        脱敏后的 API Key

    Examples:
        sk-1234567890abcdef -> sk-12...cdef
        Bearer abc123xyz -> Bearer ab...xyz
    """
    if not api_key or len(api_key) <= 8:
        return "***"

    # 保留前缀和后缀各4个字符
    return f"{api_key[:4]}...{api_key[-4:]}"
