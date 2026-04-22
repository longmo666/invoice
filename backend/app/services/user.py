from typing import List
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserListItem, UserDetail, AddQuotaRequest
from app.core.pagination import PageParams
from app.core.responses import PageResult
from app.core.exceptions import NotFoundException, ValidationException


class UserService:
    """用户服务"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_list(self, page_params: PageParams) -> PageResult[UserListItem]:
        """获取用户列表"""
        result = self.user_repo.paginate(
            page_params=page_params,
            filters={"role": UserRole.USER},
            search_fields=["username"]
        )

        return PageResult(
            items=[UserListItem.model_validate(item) for item in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages
        )

    def get_user_detail(self, user_id: int) -> UserDetail:
        """获取用户详情"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return UserDetail.model_validate(user)

    def update_user_status(self, user_id: int, status: UserStatus) -> UserDetail:
        """更新用户状态"""
        user = self.user_repo.update_status(user_id, status)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return UserDetail.model_validate(user)

    def add_user_quota(self, user_id: int, request: AddQuotaRequest) -> UserDetail:
        """增加用户额度"""
        if request.amount <= 0:
            raise ValidationException(detail="额度数量必须大于0")

        user = self.user_repo.add_quota(user_id, request.amount)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return UserDetail.model_validate(user)

    def delete_user(self, user_id: int, current_user_id: int) -> bool:
        """删除用户"""
        # 防止自删除
        if user_id == current_user_id:
            raise ValidationException(detail="不能删除自己的账号")

        # 防止删除最后一个管理员
        user = self.user_repo.get_by_id(user_id)
        if user and user.role == UserRole.ADMIN:
            admin_count = self.user_repo.count_by_role(UserRole.ADMIN)
            if admin_count <= 1:
                raise ValidationException(detail="不能删除最后一个管理员账号")

        return self.user_repo.delete(user_id)

    def batch_delete_users(self, ids: List[int], current_user_id: int) -> int:
        """批量删除用户"""
        # 防止自删除
        if current_user_id in ids:
            raise ValidationException(detail="不能删除自己的账号")

        # 防止删除所有管理员
        admin_count = self.user_repo.count_by_role(UserRole.ADMIN)
        deleting_admins = sum(
            1 for uid in ids
            if (user := self.user_repo.get_by_id(uid)) and user.role == UserRole.ADMIN
        )
        if deleting_admins >= admin_count:
            raise ValidationException(detail="不能删除所有管理员账号")

        return self.user_repo.batch_delete(ids)
