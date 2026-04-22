from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserLogin, UserDetail, TokenResponse, ChangePasswordRequest
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ValidationException
)


class AuthService:
    """认证服务"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_create: UserCreate) -> TokenResponse:
        """用户注册"""
        # 检查用户名是否已存在
        if self.user_repo.get_by_username(user_create.username):
            raise ConflictException(detail="用户名已存在")

        # 创建用户
        user = User(
            username=user_create.username,
            password_hash=get_password_hash(user_create.password),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            remaining_quota=settings.DEFAULT_USER_QUOTA,
            used_quota=0
        )
        user = self.user_repo.create(user)

        # 生成令牌
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})

        return TokenResponse(
            access_token=access_token,
            user=UserDetail.model_validate(user)
        )

    def login(self, user_login: UserLogin, require_admin: bool = False) -> TokenResponse:
        """用户登录"""
        # 查找用户
        user = self.user_repo.get_by_username(user_login.username)
        if not user:
            raise UnauthorizedException(detail="账号不存在")

        # 验证密码
        if not verify_password(user_login.password, user.password_hash):
            raise UnauthorizedException(detail="密码错误")

        # 检查状态
        if user.status == UserStatus.DISABLED:
            raise UnauthorizedException(detail="账号已禁用")

        # 检查角色
        if require_admin and user.role != UserRole.ADMIN:
            raise UnauthorizedException(detail="用户名或密码错误")

        # 更新最后登录时间
        self.user_repo.update_last_login(user.id)

        # 生成令牌
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})

        return TokenResponse(
            access_token=access_token,
            user=UserDetail.model_validate(user)
        )

    def get_current_user(self, user_id: int) -> UserDetail:
        """获取当前用户"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return UserDetail.model_validate(user)

    def change_password(self, user_id: int, request: ChangePasswordRequest) -> None:
        """修改密码"""
        # 获取用户
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")

        # 验证当前密码
        if not verify_password(request.current_password, user.password_hash):
            raise UnauthorizedException(detail="当前密码错误")

        # 检查新密码是否与旧密码相同
        if verify_password(request.new_password, user.password_hash):
            raise ValidationException(detail="新密码不能与当前密码相同")

        # 更新密码
        user.password_hash = get_password_hash(request.new_password)
        self.db.commit()
        self.db.refresh(user)
