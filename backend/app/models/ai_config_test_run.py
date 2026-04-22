from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class AIConfigTestRun(Base):
    """AI 配置样本测试运行记录"""
    __tablename__ = "ai_config_test_runs"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("ai_configs.id"), nullable=False, comment="AI 配置 ID")
    tester_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="测试人员 ID")

    # 测试文件信息
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_type = Column(String(50), nullable=False, comment="文件类型: image, pdf")
    invoice_type = Column(String(50), nullable=False, comment="发票类型: vat_special, vat_normal, railway_ticket")

    # 测试模式
    test_mode = Column(String(50), nullable=False, comment="测试模式: image_single, pdf_compare")
    tested_strategy = Column(String(50), nullable=True, comment="测试的策略: direct_pdf, convert_to_images")

    # 测试结果
    success = Column(Boolean, nullable=False, comment="是否成功")
    request_path = Column(String(500), nullable=True, comment="请求路径")
    execution_path = Column(String(500), nullable=True, comment="执行路径")
    latency_ms = Column(Integer, nullable=True, comment="延迟（毫秒）")
    error_message = Column(Text, nullable=True, comment="错误信息")
    status_code = Column(Integer, nullable=True, comment="HTTP 状态码")
    diagnostic_steps = Column(Text, nullable=True, comment="诊断步骤（JSON）")

    # 响应数据
    raw_response = Column(Text, nullable=True, comment="原始响应（JSON）")
    parsed_result = Column(Text, nullable=True, comment="解析结果（JSON）")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
