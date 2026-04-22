from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class CleaningStatusEnum(str, Enum):
    """清洗任务状态"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ArchiveTypeEnum(str, Enum):
    """压缩包类型"""
    ZIP = "zip"
    SEVENZIP = "7z"
    RAR = "rar"


class ExportTypeEnum(str, Enum):
    """导出类型"""
    IMAGE = "image"
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    PPT = "ppt"
    OFD = "ofd"
    XML = "xml"


class CleaningTaskCreate(BaseModel):
    """创建清洗任务请求"""
    selected_types: List[ExportTypeEnum] = Field(..., min_length=1, description="选择的导出类型")


class CleaningTaskDetail(BaseModel):
    """清洗任务详情"""
    id: int
    user_id: int
    original_filename: str
    archive_type: ArchiveTypeEnum
    selected_types: List[str]
    status: CleaningStatusEnum
    progress: int
    total_entries: int
    matched_count: int
    matched_by_type: Optional[Dict[str, int]] = None
    skipped_count: int
    failed_reason: Optional[str] = None
    result_zip_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CleaningTaskList(BaseModel):
    """清洗任务列表项"""
    id: int
    original_filename: str
    selected_types: List[str]
    status: CleaningStatusEnum
    progress: int
    matched_count: int
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminCleaningTaskList(CleaningTaskList):
    """管理员清洗任务列表项（包含用户信息）"""
    user_id: int
    username: Optional[str] = None

    class Config:
        from_attributes = True
