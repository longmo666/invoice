from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    """用户角色"""
    USER = "user"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    DISABLED = "disabled"


class UserCreate(BaseModel):
    """用户创建"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, description="密码")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("用户名不能为空")
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """验证密码复杂度：必须包含字母和数字"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新"""
    status: Optional[UserStatus] = None


class UserDetail(BaseModel):
    """用户详情"""
    id: int
    username: str
    role: UserRole
    status: UserStatus
    remaining_quota: int
    used_quota: int
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserListItem(BaseModel):
    """用户列表项"""
    id: int
    username: str
    role: UserRole
    status: UserStatus
    remaining_quota: int
    used_quota: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserDetail


class AddQuotaRequest(BaseModel):
    """增加额度请求"""
    amount: int = Field(..., gt=0, description="额度数量")


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: list[int] = Field(..., min_length=1, description="用户ID列表")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str = Field(..., min_length=1, description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")

    @field_validator('new_password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """验证密码复杂度：必须包含字母和数字"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
