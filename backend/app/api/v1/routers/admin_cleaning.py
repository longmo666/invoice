from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.cleaning_task import AdminCleaningTaskList
from app.services.cleaning import CleaningService
from app.api.deps import get_current_user_id, require_admin
from app.core.responses import success_response
from app.repositories.user import UserRepository

router = APIRouter(prefix="/admin/cleaning", tags=["管理员-文件清洗"])


@router.get("/tasks", response_model=dict, dependencies=[Depends(require_admin)])
def get_all_tasks(
    db: Session = Depends(get_db)
):
    """获取所有清洗任务（管理员）"""
    service = CleaningService(db)
    user_repo = UserRepository(db)

    tasks = service.get_all_tasks()

    # 添加用户名信息
    task_list = []
    for task in tasks:
        task_dict = AdminCleaningTaskList.model_validate(task).model_dump()
        user = user_repo.get_by_id(task.user_id)
        task_dict["username"] = user.username if user else "未知用户"
        task_list.append(task_dict)

    return success_response(data=task_list, message="获取成功")


@router.post("/tasks/batch-delete", response_model=dict, dependencies=[Depends(require_admin)])
def batch_delete_tasks(
    task_ids: List[int],
    db: Session = Depends(get_db)
):
    """批量删除任务（管理员）"""
    service = CleaningService(db)
    deleted_count = service.admin_delete_tasks(task_ids)
    return success_response(data={"deleted_count": deleted_count}, message=f"已删除 {deleted_count} 个任务")
