from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.ai_config import (
    AIConfigCreate,
    AIConfigUpdate,
    AIConfigDetail,
    AIConfigListItem,
    AIConfigTestResponse,
    DiagnosticStep,
)
from app.schemas.ai_config_test import (
    SampleTestResponse,
    UpdatePDFStrategyRequest
)
from app.services.ai_config_service import AIConfigService
from app.services.ai_config_test_service import AIConfigTestService
from app.api.deps import get_current_user_id, require_admin
from app.core.responses import ApiResponse, success_response, error_response

router = APIRouter(prefix="/ai-configs", tags=["AI配置管理"])


@router.post("", response_model=ApiResponse[AIConfigDetail], dependencies=[Depends(require_admin)])
async def create_ai_config(
    data: AIConfigCreate,
    db: Session = Depends(get_db)
):
    """创建 AI 配置（仅管理员）"""
    service = AIConfigService(db)
    config = service.create_config(data)

    config_detail = AIConfigDetail.model_validate(service.get_config(config.id)).model_dump()

    return success_response(data=config_detail, message="配置创建成功")


@router.get("", response_model=ApiResponse[List[AIConfigListItem]], dependencies=[Depends(require_admin)])
def list_ai_configs(
    db: Session = Depends(get_db)
):
    """获取 AI 配置列表（仅管理员）"""
    service = AIConfigService(db)
    configs = service.list_configs()

    config_list = [AIConfigListItem.model_validate(config).model_dump() for config in configs]

    return success_response(data=config_list, message="获取成功")


@router.get("/{config_id}", response_model=ApiResponse[AIConfigDetail], dependencies=[Depends(require_admin)])
def get_ai_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """获取 AI 配置详情（仅管理员）"""
    service = AIConfigService(db)
    config = service.get_config(config_id)

    if not config:
        return success_response(success=False, message="配置不存在")

    config_detail = AIConfigDetail.model_validate(config).model_dump()

    return success_response(data=config_detail, message="获取成功")


@router.put("/{config_id}", response_model=ApiResponse[AIConfigDetail], dependencies=[Depends(require_admin)])
async def update_ai_config(
    config_id: int,
    data: AIConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新 AI 配置（仅管理员）"""
    service = AIConfigService(db)
    config = service.update_config(config_id, data)

    config_detail = AIConfigDetail.model_validate(service.get_config(config.id)).model_dump()

    return success_response(data=config_detail, message="配置更新成功")


@router.delete("/{config_id}", response_model=ApiResponse, dependencies=[Depends(require_admin)])
def delete_ai_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """删除 AI 配置（仅管理员）"""
    service = AIConfigService(db)
    success = service.delete_config(config_id)

    if not success:
        return success_response(success=False, message="删除失败")

    return success_response(message="配置删除成功")


@router.post("/{config_id}/activate", response_model=ApiResponse, dependencies=[Depends(require_admin)])
def activate_ai_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """激活 AI 配置（仅管理员）"""
    service = AIConfigService(db)
    success = service.set_active(config_id)

    if not success:
        return success_response(success=False, message="激活失败")

    return success_response(message="配置激活成功")


@router.post("/{config_id}/toggle-enabled", response_model=ApiResponse, dependencies=[Depends(require_admin)])
def toggle_ai_config_enabled(
    config_id: int,
    enabled: bool = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """切换 AI 配置启用状态（仅管理员）"""
    service = AIConfigService(db)
    success = service.toggle_enabled(config_id, enabled)

    if not success:
        return success_response(success=False, message="操作失败")

    return success_response(message=f"配置已{'启用' if enabled else '禁用'}")


@router.post("/test-connection", response_model=ApiResponse[AIConfigTestResponse], dependencies=[Depends(require_admin)])
async def test_ai_connection(
    config_id: int,
    db: Session = Depends(get_db)
):
    """测试 AI 配置连接（仅管理员）"""
    service = AIConfigService(db)

    config = service.get_config(config_id)
    if not config:
        return success_response(success=False, message="配置不存在")

    result = await service.test_connection(
        provider_vendor=config.provider_vendor,
        api_style=config.api_style,
        base_url=config.base_url,
        model_name=config.model_name,
        api_key=config.api_key,
        timeout=config.timeout,
        ocr_chat_model=config.ocr_chat_model,
    )

    test_result = AIConfigTestResponse(
        success=result["success"],
        message=result["message"],
        latency_ms=result["latency_ms"],
        request_path=result["request_path"],
        status_code=result["status_code"],
        diagnostic_steps=[
            DiagnosticStep(**s) for s in result.get("diagnostic_steps", [])
        ],
    )

    return success_response(data=test_result.model_dump(), message="测试完成")


@router.post("/{config_id}/sample-test", response_model=ApiResponse[SampleTestResponse], dependencies=[Depends(require_admin)])
async def test_sample(
    config_id: int,
    file: UploadFile = File(...),
    invoice_type: str = Form(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """样本测试（仅管理员）"""
    try:
        valid_types = ['vat_special', 'vat_normal', 'railway_ticket']
        if invoice_type not in valid_types:
            return error_response(
                error=f"不支持的发票类型: {invoice_type}",
                message=f"当前仅支持: {', '.join(valid_types)}"
            )

        test_service = AIConfigTestService(db)

        file_ext = file.filename.lower().split('.')[-1]

        if file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
            result = await test_service.test_image_sample(
                config_id=config_id,
                user_id=user_id,
                file=file,
                invoice_type=invoice_type
            )
        elif file_ext == 'pdf':
            result = await test_service.test_pdf_sample(
                config_id=config_id,
                user_id=user_id,
                file=file,
                invoice_type=invoice_type
            )
        else:
            return error_response(
                error=f"不支持的文件类型: {file_ext}",
                message="仅支持图片（JPG/PNG/BMP/GIF）或 PDF 文件"
            )

        return success_response(data=result, message="测试完成")
    except ValueError as e:
        return error_response(error=str(e), message="参数错误")
    except Exception as e:
        return error_response(error=str(e), message="样本测试失败")


@router.post("/{config_id}/pdf-strategy", response_model=ApiResponse, dependencies=[Depends(require_admin)])
def update_pdf_strategy(
    config_id: int,
    data: UpdatePDFStrategyRequest,
    db: Session = Depends(get_db)
):
    """更新 PDF 策略（仅管理员）"""
    test_service = AIConfigTestService(db)
    success = test_service.update_pdf_strategy(config_id, data.pdf_strategy.value)

    if not success:
        return success_response(success=False, message="更新失败")

    return success_response(message="PDF 策略更新成功")
