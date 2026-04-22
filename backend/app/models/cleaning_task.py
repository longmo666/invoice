from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, JSON, ForeignKey
from datetime import datetime
from enum import Enum
from app.models.base import BaseModel


class CleaningStatus(str, Enum):
    """清洗任务状态"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ArchiveType(str, Enum):
    """压缩包类型"""
    ZIP = "zip"
    SEVENZIP = "7z"
    RAR = "rar"


class CleaningTask(BaseModel):
    """文件清洗任务模型"""
    __tablename__ = "cleaning_tasks"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    archive_type = Column(SQLEnum(ArchiveType), nullable=False)
    selected_types = Column(JSON, nullable=False)  # ["image", "pdf", "word", ...]
    status = Column(SQLEnum(CleaningStatus), default=CleaningStatus.UPLOADING, nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    total_entries = Column(Integer, default=0, nullable=False)
    matched_count = Column(Integer, default=0, nullable=False)
    matched_by_type = Column(JSON, nullable=True)  # {"image": 10, "pdf": 5, ...}
    skipped_count = Column(Integer, default=0, nullable=False)
    failed_reason = Column(Text, nullable=True)
    result_zip_path = Column(String(500), nullable=True)
    finished_at = Column(DateTime, nullable=True)
