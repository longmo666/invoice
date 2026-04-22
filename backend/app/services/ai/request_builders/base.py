"""
请求构建器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.services.ai.transport import TransportMode


class RequestBuilder(ABC):
    """请求构建器抽象基类"""

    @abstractmethod
    def build_request(
        self,
        prompt: str,
        transport_mode: TransportMode,
        image_data: bytes = None,
        file_data: bytes = None,
        file_name: str = None,
        file_id: str = None,
        file_url: str = None,
        model_name: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        构建请求体

        Args:
            prompt: 提示词
            transport_mode: 传输模式（TransportMode 枚举）
            image_data: 图片数据
            file_data: 文件数据（如 PDF）
            file_name: 文件名
            file_id: 文件 ID
            file_url: 文件 URL
            model_name: 模型名称
            temperature: 温度
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            请求体字典
        """
        pass
