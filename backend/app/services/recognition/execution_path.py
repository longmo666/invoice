"""
执行路径枚举

定义不同输入类型和识别模式的执行路径
"""
from enum import Enum


class RecognitionMode(str, Enum):
    """识别模式"""
    LOCAL_OCR = "local_ocr"  # 本地 OCR
    AI = "ai"  # AI 识别
    HYBRID = "hybrid"  # 混合模式


class ExecutionPath(str, Enum):
    """执行路径"""
    # AI 路径
    AI_IMAGE = "ai_image"  # AI 识别图片
    AI_PDF = "ai_pdf"  # AI 识别 PDF

    # 结构化文件路径
    XML_PARSER = "xml_parser"  # XML 解析
    OFD_PARSER = "ofd_parser"  # OFD 解析

    # 本地 OCR 路径
    LOCAL_OCR_IMAGE = "local_ocr_image"  # 本地 OCR 识别图片
    LOCAL_OCR_PDF = "local_ocr_pdf"  # 本地 OCR 识别 PDF

    # 混合路径
    HYBRID_PDF = "hybrid_pdf"  # 混合模式识别 PDF
    HYBRID_IMAGE = "hybrid_image"  # 混合模式识别图片


class ExecutionPathResolver:
    """执行路径解析器"""

    @staticmethod
    def resolve(file_type: str, recognition_mode: str) -> ExecutionPath:
        """
        根据文件类型和识别模式解析执行路径

        Args:
            file_type: 文件类型 (image, pdf, xml, ofd)
            recognition_mode: 识别模式 (local_ocr, ai, hybrid)

        Returns:
            执行路径

        Raises:
            ValueError: 不支持的组合
        """
        # 结构化文件直接解析，不受识别模式影响
        if file_type == "xml":
            return ExecutionPath.XML_PARSER
        elif file_type == "ofd":
            return ExecutionPath.OFD_PARSER

        # 根据识别模式和文件类型确定路径
        if recognition_mode == RecognitionMode.AI:
            if file_type == "image":
                return ExecutionPath.AI_IMAGE
            elif file_type == "pdf":
                return ExecutionPath.AI_PDF
        elif recognition_mode == RecognitionMode.LOCAL_OCR:
            if file_type == "image":
                return ExecutionPath.LOCAL_OCR_IMAGE
            elif file_type == "pdf":
                return ExecutionPath.LOCAL_OCR_PDF
        elif recognition_mode == RecognitionMode.HYBRID:
            if file_type == "image":
                return ExecutionPath.HYBRID_IMAGE
            elif file_type == "pdf":
                return ExecutionPath.HYBRID_PDF

        raise ValueError(f"不支持的组合: file_type={file_type}, recognition_mode={recognition_mode}")
