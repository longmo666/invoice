from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User, UserRole, UserStatus
from app.repositories.user import UserRepository

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="无效的令牌")
    return int(user_id)


def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException(detail="用户不存在")
    if user.status != UserStatus.ACTIVE:
        raise UnauthorizedException(detail="用户已被禁用")
    return user


def require_admin(
    current_user: User = Depends(get_current_user)
) -> None:
    """要求管理员权限"""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(detail="需要管理员权限")
