from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class InvoiceTypeEnum(str, Enum):
    """发票类型枚举"""
    VAT_SPECIAL = "vat_special"
    VAT_NORMAL = "vat_normal"
    RAILWAY_TICKET = "railway_ticket"


class FileTypeEnum(str, Enum):
    """文件类型枚举"""
    IMAGE = "image"
    PDF = "pdf"
    XML = "xml"
    OFD = "ofd"


class RecognitionModeEnum(str, Enum):
    """识别模式枚举"""
    LOCAL_OCR = "local_ocr"
    AI = "ai"
    HYBRID = "hybrid"


class TaskStatusEnum(str, Enum):
    """任务状态枚举"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ReviewStatusEnum(str, Enum):
    """复核状态枚举"""
    AUTO_PASSED = "auto_passed"
    PENDING_REVIEW = "pending_review"
    MANUAL_CONFIRMED = "manual_confirmed"


# ==================== 请求 Schema ====================

class RecognitionTaskCreate(BaseModel):
    """创建识别任务请求"""
    invoice_type: InvoiceTypeEnum = Field(..., description="发票类型")
    recognition_mode: RecognitionModeEnum = Field(default=RecognitionModeEnum.AI, description="识别模式")


class RecognitionItemReview(BaseModel):
    """复核识别结果请求"""
    reviewed_result: dict = Field(..., description="复核后的结果")
    review_status: ReviewStatusEnum = Field(..., description="复核状态")


class RecognitionExportRequest(BaseModel):
    """导出识别结果请求"""
    task_ids: List[int] = Field(..., min_length=1, description="任务ID列表")
    format: str = Field(..., pattern="^(excel|csv)$", description="导出格式")


# ==================== 响应 Schema ====================

class RecognitionItemDetail(BaseModel):
    """识别结果项详情"""
    id: int
    task_id: int
    page_number: Optional[int]
    item_index: int
    original_result: dict
    reviewed_result: dict
    review_status: ReviewStatusEnum
    review_reason: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class RecognitionTaskDetail(BaseModel):
    """识别任务详情"""
    id: int
    user_id: int
    original_filename: str
    file_type: FileTypeEnum
    file_path: str
    file_size: int
    invoice_type: InvoiceTypeEnum
    recognition_mode: RecognitionModeEnum
    ai_config_id: Optional[int]
    status: TaskStatusEnum
    progress: int
    total_items: int
    success_items: int
    failed_items: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    finished_at: Optional[datetime]
    items: List[RecognitionItemDetail] = []

    class Config:
        from_attributes = True


class RecognitionTaskListItem(BaseModel):
    """识别任务列表项"""
    id: int
    original_filename: str
    file_type: FileTypeEnum
    invoice_type: InvoiceTypeEnum
    status: TaskStatusEnum
    progress: int
    total_items: int
    success_items: int
    failed_items: int
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


class RecognitionTaskCreateResponse(BaseModel):
    """创建识别任务响应"""
    id: int
    status: TaskStatusEnum
    progress: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecognitionItemListItem(BaseModel):
    """识别结果项列表项（用于待复核列表）"""
    id: int
    task_id: int
    task_filename: str = ""
    invoice_type: str = ""
    page_number: Optional[int] = None
    item_index: int = 0
    original_result: dict = {}
    reviewed_result: dict = {}
    review_status: ReviewStatusEnum = ReviewStatusEnum.PENDING_REVIEW
    review_reason: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_item(cls, item) -> "RecognitionItemListItem":
        """从 ORM RecognitionItem（含 task 关系）构建，避免 router 层手工塞字段"""
        return cls(
            id=item.id,
            task_id=item.task_id,
            task_filename=item.task.original_filename if item.task else "",
            invoice_type=item.task.invoice_type.value if item.task else "",
            page_number=item.page_number,
            item_index=item.item_index,
            original_result=item.original_result or {},
            reviewed_result=item.reviewed_result or {},
            review_status=item.review_status.value if item.review_status else "pending_review",
            review_reason=item.review_reason,
            confidence_score=float(item.confidence_score) if item.confidence_score is not None else None,
            created_at=item.created_at,
        )


# ==================== 管理端分页摘要 Schema ====================

class AdminTaskSummary(BaseModel):
    """管理端任务摘要（服务端聚合，含可抵扣税额）"""
    # 发票字段
    invoice_number: str = ""
    invoice_date: str = ""
    buyer_name: str = ""
    seller_name: str = ""
    total_amount: str = ""
    # 高铁票字段
    train_number: str = ""
    departure_station: str = ""
    train_date: str = ""
    ticket_price: str = ""
    passenger_name: str = ""
    ticket_id: str = ""
    seat_class: str = ""
    # 统一计算
    deductible_tax: str = ""


class AdminPaginatedTaskItem(BaseModel):
    """管理端分页任务列表项"""
    id: int
    user_id: int
    username: str
    original_filename: str
    invoice_type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    summary: AdminTaskSummary = AdminTaskSummary()


class AdminPaginatedTasksResponse(BaseModel):
    """管理端分页任务列表响应"""
    items: List[AdminPaginatedTaskItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== 用户侧补充 Schema ====================

class BatchDeleteTasksRequest(BaseModel):
    """批量删除任务请求"""
    task_ids: List[int] = Field(..., min_length=1, description="任务 ID 列表")


class BatchDeleteResult(BaseModel):
    """批量删除结果"""
    deleted: int = Field(..., description="成功删除数量")


class UserPaginatedTaskItem(BaseModel):
    """用户侧分页任务列表项（含摘要）"""
    id: int
    original_filename: str = ""
    file_type: Optional[str] = None
    invoice_type: Optional[str] = None
    status: Optional[str] = None
    progress: int = 0
    total_items: int = 0
    success_items: int = 0
    failed_items: int = 0
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    finished_at: Optional[str] = None
    confidence_score: Optional[float] = None
    review_status: Optional[str] = None
    summary: dict = {}


class UserPaginatedTasksResponse(BaseModel):
    """用户侧分页任务列表响应"""
    items: List[UserPaginatedTaskItem]
    total: int
    page: int
    page_size: int
