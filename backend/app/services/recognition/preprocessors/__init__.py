from pathlib import Path
from typing import Optional
from app.services.recognition.preprocessors.base import FilePreprocessor, PreprocessorResult
from app.services.recognition.preprocessors.image_preprocessor import ImagePreprocessor
from app.services.recognition.preprocessors.pdf_preprocessor import PDFPreprocessor
from app.services.recognition.preprocessors.xml_parser import XMLParser
from app.services.recognition.preprocessors.ofd_preprocessor import OFDPreprocessor


class PreprocessorFactory:
    """预处理器工厂"""

    _preprocessors = {
        "image": ImagePreprocessor(),
        "pdf": PDFPreprocessor(),
        "xml": XMLParser(),
        "ofd": OFDPreprocessor()
    }

    @classmethod
    def get_preprocessor(cls, file_type: str) -> Optional[FilePreprocessor]:
        """
        获取预处理器

        Args:
            file_type: 文件类型 (image, pdf, xml, ofd)

        Returns:
            预处理器实例，如果不支持则返回 None
        """
        return cls._preprocessors.get(file_type)

    @classmethod
    async def preprocess_file(cls, file_path: Path, file_type: str) -> PreprocessorResult:
        """
        预处理文件

        Args:
            file_path: 文件路径
            file_type: 文件类型

        Returns:
            预处理结果

        Raises:
            ValueError: 不支持的文件类型
        """
        preprocessor = cls.get_preprocessor(file_type)
        if not preprocessor:
            raise ValueError(f"不支持的文件类型: {file_type}")

        return await preprocessor.preprocess(file_path)


__all__ = [
    "FilePreprocessor",
    "PreprocessorResult",
    "ImagePreprocessor",
    "PDFPreprocessor",
    "XMLParser",
    "OFDPreprocessor",
    "PreprocessorFactory"
]
