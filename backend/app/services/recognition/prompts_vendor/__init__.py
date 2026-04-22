"""
提示词路由

每个厂商的提示词独立维护在各自文件中，互不影响。
"""
from app.services.recognition.prompts_vendor.openai import PROMPTS as OPENAI_PROMPTS
from app.services.recognition.prompts_vendor.anthropic import PROMPTS as ANTHROPIC_PROMPTS
from app.services.recognition.prompts_vendor.gemini import PROMPTS as GEMINI_PROMPTS
from app.services.recognition.prompts_vendor.zhipu import PROMPTS as ZHIPU_PROMPTS

_VENDOR_PROMPTS = {
    "openai_compatible": OPENAI_PROMPTS,
    "anthropic_compatible": ANTHROPIC_PROMPTS,
    "google_compatible": GEMINI_PROMPTS,
    "zhipu_compatible": ZHIPU_PROMPTS,
}


def get_prompt_template(invoice_type: str, provider_type: str) -> str:
    """
    获取提示词模板

    Args:
        invoice_type: 发票类型 (vat_special, vat_normal, railway_ticket)
        provider_type: 提供商厂商

    Returns:
        提示词模板字符串
    """
    if invoice_type in ("vat_special", "vat_normal"):
        category = "vat"
    elif invoice_type == "railway_ticket":
        category = "railway"
    else:
        raise ValueError(f"不支持的发票类型: {invoice_type}")

    vendor_prompts = _VENDOR_PROMPTS.get(provider_type, OPENAI_PROMPTS)
    return vendor_prompts[category]
