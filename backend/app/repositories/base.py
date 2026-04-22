from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.base import BaseModel
from app.core.pagination import PageParams
from app.core.responses import PageResult

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """基础仓储"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据ID获取"""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False
        ).first()

    def list(
        self,
        page_params: Optional[PageParams] = None,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """列表查询"""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        # 分页
        if page_params:
            offset = (page_params.page - 1) * page_params.page_size
            query = query.offset(offset).limit(page_params.page_size)

        return query.all()

    def paginate(
        self,
        page_params: PageParams,
        filters: Optional[dict] = None,
        search_fields: Optional[List[str]] = None
    ) -> PageResult[ModelType]:
        """分页查询"""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        # 搜索
        if page_params.search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).like(f"%{page_params.search}%")
                    )
            if search_conditions:
                query = query.filter(or_(*search_conditions))

        # 排序
        if page_params.sort_by and hasattr(self.model, page_params.sort_by):
            sort_column = getattr(self.model, page_params.sort_by)
            if page_params.sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

        # 总数
        total = query.count()

        # 分页
        offset = (page_params.page - 1) * page_params.page_size
        items = query.offset(offset).limit(page_params.page_size).all()

        total_pages = (total + page_params.page_size - 1) // page_params.page_size

        return PageResult(
            items=items,
            total=total,
            page=page_params.page,
            page_size=page_params.page_size,
            total_pages=total_pages
        )

    def create(self, obj: ModelType) -> ModelType:
        """创建"""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """更新"""
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """软删除"""
        obj = self.get_by_id(id)
        if obj:
            obj.is_deleted = True
            self.db.commit()
            return True
        return False

    def hard_delete(self, id: int) -> bool:
        """硬删除"""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def exists(self, filters: dict) -> bool:
        """检查是否存在"""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None
