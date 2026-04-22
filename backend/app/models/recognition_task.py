from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base


class InvoiceType(str, enum.Enum):
    """发票类型枚举"""
    VAT_SPECIAL = "vat_special"  # 增值税专用发票
    VAT_NORMAL = "vat_normal"    # 增值税普通发票
    RAILWAY_TICKET = "railway_ticket"  # 高铁票


class FileType(str, enum.Enum):
    """文件类型枚举"""
    IMAGE = "image"
    PDF = "pdf"
    XML = "xml"
    OFD = "ofd"


class RecognitionMode(str, enum.Enum):
    """识别模式枚举"""
    LOCAL_OCR = "local_ocr"
    AI = "ai"
    HYBRID = "hybrid"


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class RecognitionTask(Base):
    """识别任务模型（任务级别）"""
    __tablename__ = "recognition_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户 ID")

    # 文件信息
    original_filename = Column(String(500), nullable=False, comment="原始文件名")
    file_type = Column(Enum(FileType), nullable=False, comment="文件类型")
    file_path = Column(String(1000), nullable=False, comment="文件存储路径")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")

    # 识别配置
    invoice_type = Column(Enum(InvoiceType), nullable=False, comment="发票类型")
    recognition_mode = Column(Enum(RecognitionMode), nullable=False, comment="识别模式")
    ai_config_id = Column(Integer, ForeignKey("ai_configs.id"), nullable=True, comment="使用的 AI 配置 ID")

    # 任务状态
    status = Column(Enum(TaskStatus), default=TaskStatus.UPLOADING, nullable=False, index=True, comment="任务状态")
    progress = Column(Integer, default=0, comment="进度百分比 0-100")

    # 结果统计
    total_items = Column(Integer, default=0, comment="识别出的总项数")
    success_items = Column(Integer, default=0, comment="成功项数")
    failed_items = Column(Integer, default=0, comment="失败项数")

    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="软删除时间")

    # 关系
    items = relationship("RecognitionItem", back_populates="task", cascade="all, delete-orphan")
