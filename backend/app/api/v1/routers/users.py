from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import (
    UserListItem,
    UserDetail,
    AddQuotaRequest,
    BatchDeleteRequest,
    UserStatus
)
from app.models.user import User
from app.services.user import UserService
from app.api.deps import require_admin, get_current_user
from app.core.pagination import PageParams
from app.core.responses import success_response, PageResult

router = APIRouter(prefix="/admin/users", tags=["用户管理"])


@router.get("", response_model=dict)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
):
    """获取用户列表"""
    page_params = PageParams(page=page, page_size=page_size, search=search)
    user_service = UserService(db)
    result = user_service.get_user_list(page_params)
    return success_response(data=result.model_dump(), message="获取成功")


@router.get("/{user_id}", response_model=dict)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
):
    """获取用户详情"""
    user_service = UserService(db)
    user = user_service.get_user_detail(user_id)
    return success_response(data=user.model_dump(), message="获取成功")


@router.patch("/{user_id}/status", response_model=dict)
def update_user_status(
    user_id: int,
    status: UserStatus,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
):
    """更新用户状态"""
    user_service = UserService(db)
    user = user_service.update_user_status(user_id, status)
    return success_response(data=user.model_dump(), message="状态更新成功")


@router.post("/{user_id}/quota", response_model=dict)
def add_user_quota(
    user_id: int,
    request: AddQuotaRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
):
    """增加用户额度"""
    user_service = UserService(db)
    user = user_service.add_user_quota(user_id, request)
    return success_response(data=user.model_dump(), message="额度添加成功")


@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin)
):
    """删除用户"""
    user_service = UserService(db)
    user_service.delete_user(user_id, current_user.id)
    return success_response(message="删除成功")


@router.post("/batch-delete", response_model=dict)
def batch_delete_users(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin)
):
    """批量删除用户"""
    user_service = UserService(db)
    count = user_service.batch_delete_users(request.ids, current_user.id)
    return success_response(data={"count": count}, message=f"成功删除 {count} 个用户")
