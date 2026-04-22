from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SampleTestModeEnum(str, Enum):
    """样本测试模式枚举"""
    IMAGE_SINGLE = "image_single"
    PDF_COMPARE = "pdf_compare"


class PDFStrategyEnum(str, Enum):
    """PDF 处理策略枚举"""
    DIRECT_PDF = "direct_pdf"
    CONVERT_TO_IMAGES = "convert_to_images"


# ==================== 请求 Schema ====================

class SampleTestRequest(BaseModel):
    """样本测试请求"""
    config_id: int = Field(..., description="AI 配置 ID")
    invoice_type: str = Field(..., description="发票类型: vat_special, vat_normal, railway_ticket")


# ==================== 响应 Schema ====================

class DiagnosticStepItem(BaseModel):
    """诊断步骤项"""
    step: str = Field(..., description="步骤名称")
    url: str = Field("", description="请求 URL")
    status_code: Optional[int] = Field(None, description="HTTP 状态码")
    latency_ms: Optional[int] = Field(None, description="延迟（毫秒）")
    success: bool = Field(False, description="是否成功")
    detail: str = Field("", description="详情")


class SampleTestResult(BaseModel):
    """单次样本测试结果"""
    success: bool = Field(..., description="是否成功")
    strategy: Optional[str] = Field(None, description="使用的策略")
    latency_ms: Optional[int] = Field(None, description="延迟（毫秒）")
    request_path: Optional[str] = Field(None, description="请求路径")
    execution_path: Optional[str] = Field(None, description="执行路径")
    status_code: Optional[int] = Field(None, description="HTTP 状态码")
    error_message: Optional[str] = Field(None, description="错误信息")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="原始响应")
    structured_result: Optional[Dict[str, Any]] = Field(None, description="结构化结果")
    diagnostic_steps: List[DiagnosticStepItem] = Field(default_factory=list, description="诊断步骤")


class SampleTestResponse(BaseModel):
    """样本测试响应"""
    test_mode: SampleTestModeEnum = Field(..., description="测试模式")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    invoice_type: str = Field(..., description="发票类型")

    # 单次测试结果（图片）
    result: Optional[SampleTestResult] = Field(None, description="单次测试结果")

    # 对比测试结果（PDF）
    direct_pdf_result: Optional[SampleTestResult] = Field(None, description="直传 PDF 结果")
    convert_to_images_result: Optional[SampleTestResult] = Field(None, description="转图片结果")

    # 推荐策略（PDF）
    recommended_strategy: Optional[str] = Field(None, description="推荐策略")
    recommendation_reason: Optional[str] = Field(None, description="推荐原因")


class UpdatePDFStrategyRequest(BaseModel):
    """更新 PDF 策略请求"""
    pdf_strategy: PDFStrategyEnum = Field(..., description="PDF 处理策略")
