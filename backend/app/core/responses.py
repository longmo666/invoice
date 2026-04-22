from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应格式"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None


class PageResult(BaseModel, Generic[T]):
    """分页结果"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def success_response(data: Any = None, message: str = "操作成功", success: bool = True) -> dict:
    """成功响应"""
    return {
        "success": success,
        "data": data,
        "message": message,
        "error": None
    }


def error_response(error: str, message: str = "操作失败") -> dict:
    """错误响应"""
    return {
        "success": False,
        "data": None,
        "message": message,
        "error": error
    }
