from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from datetime import datetime
from enum import Enum
from app.models.base import BaseModel


class UserRole(str, Enum):
    """用户角色"""
    USER = "user"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    DISABLED = "disabled"


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    remaining_quota = Column(Integer, default=20, nullable=False)
    used_quota = Column(Integer, default=0, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
