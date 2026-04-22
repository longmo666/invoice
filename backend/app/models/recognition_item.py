from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey, JSON, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base


class ReviewStatus(str, enum.Enum):
    """复核状态枚举"""
    AUTO_PASSED = "auto_passed"      # 自动通过
    PENDING_REVIEW = "pending_review"  # 待人工复核
    MANUAL_CONFIRMED = "manual_confirmed"  # 人工已确认


class RecognitionItem(Base):
    """识别结果项模型（单张发票级别）"""
    __tablename__ = "recognition_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("recognition_tasks.id"), nullable=False, index=True, comment="所属任务 ID")

    # 在多页文档中的位置
    page_number = Column(Integer, nullable=True, comment="页码（PDF 多页时使用）")
    item_index = Column(Integer, nullable=False, comment="在任务中的索引（从 0 开始）")

    # 原始识别结果（JSON 格式，保存 AI 返回的完整数据）
    raw_response = Column(JSON, nullable=True, comment="AI 原始响应")
    original_result = Column(JSON, nullable=False, comment="结构化的原始识别结果")

    # 复核后的结果（JSON 格式，初始与 original_result 相同）
    reviewed_result = Column(JSON, nullable=False, comment="复核后的结果")

    # 复核状态
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.AUTO_PASSED, nullable=False, index=True, comment="复核状态")
    review_reason = Column(String(500), nullable=True, comment="待复核原因")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="复核人 ID")
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment="复核时间")

    # 置信度（0-1）
    confidence_score = Column(Numeric(3, 2), nullable=True, comment="置信度分数")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="软删除时间")

    # 关系
    task = relationship("RecognitionTask", back_populates="items")
