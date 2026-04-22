from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """基础业务异常"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseAppException):
    """资源不存在"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(BaseAppException):
    """未授权"""
    def __init__(self, detail: str = "未授权"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BaseAppException):
    """无权限"""
    def __init__(self, detail: str = "无权限访问"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ConflictException(BaseAppException):
    """冲突"""
    def __init__(self, detail: str = "资源冲突"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ValidationException(BaseAppException):
    """验证失败"""
    def __init__(self, detail: str = "验证失败"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
