from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./invoice.db"

    # Security
    SECRET_KEY: str  # 必须从环境变量读取，无默认值
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240  # 4小时，从24小时缩短

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # App
    APP_NAME: str = "Invoice Platform"
    DEBUG: bool = True

    # User defaults
    DEFAULT_USER_QUOTA: int = 20

    # Storage
    STORAGE_BASE_DIR: str = "./storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 验证 SECRET_KEY 强度
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY 长度必须至少 32 个字符")
        if self.SECRET_KEY in ["your-secret-key-change-in-production", "secret", "changeme"]:
            raise ValueError("SECRET_KEY 不能使用默认值或弱密钥")


def generate_secret_key() -> str:
    """生成强随机密钥"""
    return secrets.token_urlsafe(32)


settings = Settings()
