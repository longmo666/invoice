"""初始化管理员账号"""
import os
import secrets
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash


def generate_strong_password() -> str:
    """生成强随机密码"""
    # 生成包含字母、数字的16位随机密码
    return secrets.token_urlsafe(12)


def init_admin():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")

    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # CRITICAL FIX: 从环境变量读取管理员密码，或生成强随机密码
            admin_password = os.getenv("ADMIN_PASSWORD")
            if not admin_password:
                admin_password = generate_strong_password()
                print(f"⚠️  未设置 ADMIN_PASSWORD 环境变量，已生成随机密码")

            admin = User(
                username="admin",
                password_hash=get_password_hash(admin_password),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                remaining_quota=9999,
                used_quota=0
            )
            db.add(admin)
            db.commit()
            print(f"✅ 管理员账号创建成功")
            print(f"   用户名: admin")
            print(f"   密码: {admin_password}")
            print(f"   ⚠️  请立即修改密码或设置 ADMIN_PASSWORD 环境变量！")
        else:
            print("ℹ️  管理员账号已存在")
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
