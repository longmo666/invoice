from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from urllib.parse import quote
from pathlib import Path
from app.db.session import get_db
from app.schemas.recognition import (
    RecognitionTaskDetail,
    RecognitionTaskListItem,
    RecognitionTaskCreateResponse,
    RecognitionItemDetail,
    RecognitionItemReview,
    RecognitionItemListItem,
    BatchDeleteTasksRequest,
    BatchDeleteResult,
    UserPaginatedTasksResponse,
)
from app.services.recognition_service import RecognitionService
from app.services.export_service import ExportService
from app.api.deps import get_current_user_id
from app.core.responses import ApiResponse, success_response, error_response
from app.models.recognition_task import InvoiceType, TaskStatus, RecognitionMode
from app.models.recognition_item import ReviewStatus

router = APIRouter(prefix="/recognition", tags=["发票识别"])


@router.post("/tasks", response_model=ApiResponse[RecognitionTaskCreateResponse])
async def create_recognition_task(
    file: UploadFile = File(...),
    invoice_type: str = Form(...),
    recognition_mode: str = Form(default="ai"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建识别任务"""
    # 转换枚举
    try:
        invoice_type_enum = InvoiceType(invoice_type)
        recognition_mode_enum = RecognitionMode(recognition_mode)
    except ValueError as e:
        return error_response(error=str(e), message="参数错误")

    service = RecognitionService(db)
    task = await service.create_task(user_id, file, invoice_type_enum, recognition_mode_enum)

    response_data = RecognitionTaskCreateResponse.model_validate(task).model_dump()
    return success_response(data=response_data, message="任务创建成功")


@router.get("/tasks", response_model=ApiResponse[List[RecognitionTaskListItem]])
def list_recognition_tasks(
    invoice_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取识别任务列表"""
    # 转换枚举
    invoice_type_enum = InvoiceType(invoice_type) if invoice_type else None
    status_enum = TaskStatus(status) if status else None

    service = RecognitionService(db)
    tasks = service.list_tasks(user_id, invoice_type_enum, status_enum, limit)

    task_list = [RecognitionTaskListItem.model_validate(t).model_dump() for t in tasks]
    return success_response(data=task_list, message="获取成功")


@router.get("/tasks/paginated", response_model=ApiResponse[UserPaginatedTasksResponse])
def list_recognition_tasks_paginated(
    invoice_type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """分页获取识别任务列表（服务端聚合摘要，避免 N+1）"""
    invoice_type_enum = InvoiceType(invoice_type) if invoice_type else None
    status_enum = TaskStatus(status) if status else None

    service = RecognitionService(db)
    result = service.list_tasks_paginated(
        user_id, invoice_type_enum, status_enum, keyword, page, page_size
    )
    return success_response(data=result, message="获取成功")


@router.post("/tasks/batch-delete", response_model=ApiResponse[BatchDeleteResult])
def batch_delete_recognition_tasks(
    request: BatchDeleteTasksRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """批量物理删除识别任务"""
    service = RecognitionService(db)
    deleted = service.batch_delete_tasks(request.task_ids, user_id)
    return success_response(data={"deleted": deleted}, message=f"成功删除 {deleted} 条任务")


@router.get("/tasks/{task_id}", response_model=ApiResponse[RecognitionTaskDetail])
def get_recognition_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取识别任务详情"""
    service = RecognitionService(db)
    task = service.get_task(task_id, user_id)

    if not task:
        return error_response(error="任务不存在", message="获取失败")

    task_detail = RecognitionTaskDetail.model_validate(task).model_dump()
    return success_response(data=task_detail, message="获取成功")


@router.get("/pending-review", response_model=ApiResponse[List[RecognitionItemListItem]])
def get_pending_review_items(
    invoice_type: Optional[str] = None,
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取待复核的识别结果项，可按 invoice_type 过滤"""
    service = RecognitionService(db)
    items = service.get_pending_review_items(user_id, invoice_type=invoice_type, limit=limit)

    item_list = [
        RecognitionItemListItem.from_orm_item(item).model_dump()
        for item in items
    ]

    return success_response(data=item_list, message="获取成功")


@router.put("/items/{item_id}/review", response_model=ApiResponse[None])
def update_item_review(
    item_id: int,
    review_data: RecognitionItemReview,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新识别结果复核"""
    # 转换枚举
    review_status_enum = ReviewStatus(review_data.review_status.value)

    service = RecognitionService(db)
    success = service.update_review(
        item_id,
        user_id,
        review_data.reviewed_result,
        review_status_enum
    )

    if not success:
        return error_response(error="更新失败", message="复核失败")

    return success_response(message="复核成功")


@router.delete("/items/{item_id}", response_model=ApiResponse[None])
def void_recognition_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """作废识别结果项（物理删除）"""
    service = RecognitionService(db)
    success = service.void_item(item_id, user_id)
    if not success:
        return error_response(error="作废失败", message="项目不存在或无权限")
    return success_response(message="作废成功")


@router.get("/tasks/{task_id}/export/csv")
def export_task_to_csv(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """导出任务识别结果为 CSV"""
    # 验证任务权限
    recognition_service = RecognitionService(db)
    task = recognition_service.get_task(task_id, user_id)

    if not task:
        return error_response(error="任务不存在或无权限", message="导出失败")

    # 导出
    export_service = ExportService(db)
    csv_data = export_service.export_to_csv(task_id, task.invoice_type.value)

    # 返回文件流
    safe_filename = quote(f"{task.original_filename}_export.csv")
    return StreamingResponse(
        csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
        }
    )


@router.get("/tasks/{task_id}/export/excel")
def export_task_to_excel(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """导出任务识别结果为 Excel"""
    # 验证任务权限
    recognition_service = RecognitionService(db)
    task = recognition_service.get_task(task_id, user_id)

    if not task:
        return error_response(error="任务不存在或无权限", message="导出失败")

    # 导出
    export_service = ExportService(db)
    excel_data = export_service.export_to_excel(task_id, task.invoice_type.value)

    # 返回文件流
    safe_filename = quote(f"{task.original_filename}_export.xlsx")
    return StreamingResponse(
        excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
        }
    )


@router.get("/tasks/{task_id}/preview")
def preview_task_file(
    task_id: int,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """预览任务的原始上传文件（支持 query param token 认证，供 img/iframe 使用）"""
    from app.core.security import decode_access_token

    # 从 query param 获取 token
    if not token:
        return error_response(error="未提供认证令牌", message="预览失败")

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception:
        return error_response(error="无效的令牌", message="预览失败")

    service = RecognitionService(db)
    task = service.get_task(task_id, user_id)
    if not task or not task.file_path:
        return error_response(error="文件不存在", message="预览失败")

    file_path = Path(task.file_path)
    if not file_path.exists():
        return error_response(error="文件已被清理", message="预览失败")

    # 根据文件类型设置 MIME
    ext = file_path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".bmp": "image/bmp", ".webp": "image/webp",
        ".tiff": "image/tiff", ".tif": "image/tiff",
        ".pdf": "application/pdf",
        ".xml": "text/xml", ".ofd": "application/octet-stream",
    }
    media_type = mime_map.get(ext, "application/octet-stream")
    # 预览用 inline 模式，不触发下载
    safe_filename = quote(task.original_filename)
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{safe_filename}"}
    )


@router.delete("/tasks/{task_id}", response_model=ApiResponse[None])
def delete_recognition_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """物理删除识别任务（用户只能删自己的）"""
    service = RecognitionService(db)
    success = service.delete_task(task_id, user_id)
    if not success:
        return error_response(error="任务不存在或无权限", message="删除失败")
    return success_response(message="删除成功")
