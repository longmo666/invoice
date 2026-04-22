from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.cleaning_task import (
    CleaningTaskCreate,
    CleaningTaskDetail,
    CleaningTaskList,
    ExportTypeEnum
)
from app.services.cleaning import CleaningService
from app.api.deps import get_current_user_id
from app.core.responses import success_response, error_response

router = APIRouter(prefix="/cleaning", tags=["文件清洗"])


@router.post("/tasks", response_model=dict)
async def create_cleaning_task(
    file: UploadFile = File(...),
    selected_types: str = Form(...),  # JSON string: ["image", "pdf", ...]
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建文件清洗任务"""
    import json
    selected_types_list = json.loads(selected_types)

    # 验证类型
    valid_types = [t.value for t in ExportTypeEnum]
    for t in selected_types_list:
        if t not in valid_types:
            return success_response(success=False, message=f"不支持的导出类型: {t}")

    service = CleaningService(db)
    task = await service.create_task(user_id, file, selected_types_list)
    return success_response(data=CleaningTaskDetail.model_validate(task).model_dump(), message="任务创建成功")


@router.get("/tasks", response_model=dict)
def get_user_tasks(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取用户的任务列表"""
    service = CleaningService(db)
    tasks = service.get_user_tasks(user_id)
    task_list = [CleaningTaskList.model_validate(t).model_dump() for t in tasks]
    return success_response(data=task_list, message="获取成功")


@router.get("/tasks/{task_id}", response_model=dict)
def get_task_detail(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    service = CleaningService(db)
    task = service.get_task_detail(task_id, user_id)
    return success_response(data=CleaningTaskDetail.model_validate(task).model_dump(), message="获取成功")


@router.get("/tasks/{task_id}/download")
def download_result(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """下载清洗结果"""
    service = CleaningService(db)
    task = service.get_task_detail(task_id, user_id)

    if not task.result_zip_path:
        return success_response(success=False, message="结果文件不存在")

    from pathlib import Path
    result_path = Path(task.result_zip_path)
    if not result_path.exists():
        return success_response(success=False, message="结果文件已被清理")

    return FileResponse(
        path=str(result_path),
        filename=f"cleaned_{task.original_filename}",
        media_type="application/zip"
    )


@router.post("/tasks/{task_id}/retry", response_model=dict)
def retry_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """重试失败的任务"""
    service = CleaningService(db)
    task = service.retry_task(task_id, user_id)
    return success_response(data=CleaningTaskDetail.model_validate(task).model_dump(), message="任务已重新开始")


@router.delete("/tasks/{task_id}", response_model=dict)
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除任务"""
    service = CleaningService(db)
    service.delete_task(task_id, user_id)
    return success_response(message="删除成功")


@router.delete("/tasks", response_model=dict)
def batch_delete_tasks(
    task_ids: List[int] = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """用户批量删除自己的清洗任务"""
    service = CleaningService(db)
    deleted = 0
    for task_id in task_ids:
        try:
            service.delete_task(task_id, user_id)
            deleted += 1
        except Exception:
            continue
    return success_response(data={"deleted": deleted}, message=f"已删除 {deleted} 条")
