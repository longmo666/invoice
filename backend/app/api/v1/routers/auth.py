from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserDetail, ChangePasswordRequest
from app.services.auth import AuthService
from app.api.deps import get_current_user_id
from app.core.responses import success_response

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=dict)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    auth_service = AuthService(db)
    result = auth_service.register(user_create)
    return success_response(data=result.model_dump(), message="注册成功")


@router.post("/login", response_model=dict)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)
    result = auth_service.login(user_login, require_admin=False)
    return success_response(data=result.model_dump(), message="登录成功")


@router.post("/admin-login", response_model=dict)
def admin_login(user_login: UserLogin, db: Session = Depends(get_db)):
    """管理员登录"""
    auth_service = AuthService(db)
    result = auth_service.login(user_login, require_admin=True)
    return success_response(data=result.model_dump(), message="登录成功")


@router.get("/me", response_model=dict)
def get_me(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(user_id)
    return success_response(data=user.model_dump(), message="获取成功")


@router.post("/logout", response_model=dict)
def logout():
    """登出（前端清除token即可）"""
    return success_response(message="登出成功")


@router.post("/change-password", response_model=dict)
def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """修改密码"""
    auth_service = AuthService(db)
    auth_service.change_password(user_id, request)
    return success_response(message="密码修改成功")
