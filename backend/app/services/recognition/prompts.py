"""
提示词路由（向后兼容入口）

实际提示词已拆分到 prompts_vendor/ 目录下，每个厂商独立维护。
本文件仅保留 get_prompt_template 接口供外部调用。
"""
from app.services.recognition.prompts_vendor import get_prompt_template

__all__ = ["get_prompt_template"]
