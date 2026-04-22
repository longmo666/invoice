from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path


class PreprocessorResult:
    """预处理结果"""

    def __init__(self, images: List[bytes], metadata: Dict[str, Any] = None):
        """
        Args:
            images: 图片二进制数据列表（每个元素代表一页/一张发票）
            metadata: 元数据（如页码、原始文件信息等）
        """
        self.images = images
        self.metadata = metadata or {}


class FilePreprocessor(ABC):
    """文件预处理器抽象基类"""

    @abstractmethod
    async def preprocess(self, file_path: Path) -> PreprocessorResult:
        """
        预处理文件

        Args:
            file_path: 文件路径

        Returns:
            预处理结果
        """
        pass

    @abstractmethod
    def supports_file_type(self, file_type: str) -> bool:
        """
        检查是否支持该文件类型

        Args:
            file_type: 文件类型 (image, pdf, xml, ofd)

        Returns:
            是否支持
        """
        pass
