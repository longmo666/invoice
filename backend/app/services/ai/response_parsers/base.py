"""
响应解析器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class StandardResponse:
    """标准化响应"""
    content: str  # 响应内容
    model: str  # 使用的模型
    usage: Dict[str, int]  # token 使用情况
    finish_reason: str = None  # 结束原因


class ResponseParser(ABC):
    """响应解析器抽象基类"""

    @abstractmethod
    def parse(self, response_data: Dict[str, Any]) -> StandardResponse:
        """
        解析响应

        Args:
            response_data: 原始响应数据

        Returns:
            标准化响应
        """
        pass
