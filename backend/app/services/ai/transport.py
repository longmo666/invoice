"""
AI 传输模式枚举

所有 API 风格共享的传输模式定义。
"""
from enum import Enum


class TransportMode(str, Enum):
    """传输模式"""
    MULTIMODAL_IMAGE = "multimodal_image"  # 图片多模态
    DOCUMENT_FILE = "document_file"  # 文档文件
    TEXT_ONLY = "text_only"  # 纯文本
