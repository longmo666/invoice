"""管理员识别任务接口（从 recognition.py 拆分）"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import quote
from app.db.session import get_db
from app.schemas.recognition import RecognitionTaskDetail, AdminPaginatedTasksResponse
from app.services.recognition_service import RecognitionService
from app.services.export_service import ExportService
from app.api.deps import require_admin
from app.core.responses import ApiResponse, success_response, error_response
from app.models.recognition_task import InvoiceType, TaskStatus

router = APIRouter(prefix="/recognition/admin", tags=["管理员-发票识别"], dependencies=[Depends(require_admin)])

# ==================== tab / invoice_type 合法组合 ====================
_TAB_ALLOWED_TYPES = {
    "invoice": {"vat_special", "vat_normal"},
    "train": {"railway_ticket"},
}


@router.get("/tasks/paginated", response_model=ApiResponse[AdminPaginatedTasksResponse])
def admin_list_tasks_paginated(
    tab: str = Query(..., regex="^(invoice|train)$"),
    invoice_type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """管理端分页获取任务列表（含摘要 + 可抵扣税额，消除 N+1）"""
    # tab 与 invoice_type 冲突校验
    if invoice_type and invoice_type not in _TAB_ALLOWED_TYPES.get(tab, set()):
        return error_response(
            error=f"tab={tab} 不允许 invoice_type={invoice_type}",
            message="参数冲突"
        )

    service = RecognitionService(db)
    result = service.admin_list_tasks_paginated(
        tab=tab,
        invoice_type=invoice_type,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result, message="获取成功")



@router.get("/tasks/{task_id}", response_model=ApiResponse[RecognitionTaskDetail])
def admin_get_task_detail(
    task_id: int,
    db: Session = Depends(get_db)
):
    """管理员获取任务详情（不限用户）"""
    service = RecognitionService(db)
    task = service.admin_get_task(task_id)
    if not task:
        return error_response(error="任务不存在", message="获取失败")
    task_detail = RecognitionTaskDetail.model_validate(task).model_dump()
    return success_response(data=task_detail, message="获取成功")


@router.delete("/tasks", response_model=ApiResponse)
def admin_delete_tasks(
    task_ids: List[int] = Query(...),
    db: Session = Depends(get_db)
):
    """管理员批量物理删除任务"""
    service = RecognitionService(db)
    deleted = service.admin_delete_tasks(task_ids)
    return success_response(data={"deleted": deleted}, message=f"已删除 {deleted} 条")


@router.get("/tasks/{task_id}/export/csv")
def admin_export_csv(
    task_id: int,
    db: Session = Depends(get_db)
):
    """管理员导出 CSV（不限用户）"""
    service = RecognitionService(db)
    task = service.admin_get_task(task_id)
    if not task:
        return error_response(error="任务不存在", message="导出失败")

    export_service = ExportService(db)
    csv_data = export_service.export_to_csv(task_id, task.invoice_type.value)
    safe_filename = quote(f"{task.original_filename}_export.csv")
    return StreamingResponse(
        csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"}
    )


@router.get("/tasks/{task_id}/export/excel")
def admin_export_excel(
    task_id: int,
    db: Session = Depends(get_db)
):
    """管理员导出 Excel（不限用户）"""
    service = RecognitionService(db)
    task = service.admin_get_task(task_id)
    if not task:
        return error_response(error="任务不存在", message="导出失败")

    export_service = ExportService(db)
    excel_data = export_service.export_to_excel(task_id, task.invoice_type.value)
    safe_filename = quote(f"{task.original_filename}_export.xlsx")
    return StreamingResponse(
        excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"}
    )
