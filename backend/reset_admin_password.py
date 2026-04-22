#!/usr/bin/env python3
"""
管理员密码重置工具

用法：
  python reset_admin_password.py <新密码>

示例：
  python reset_admin_password.py admin123
"""
import sys
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def reset_admin_password(new_password: str):
    """重置管理员密码"""
    if not new_password:
        print("❌ 错误：密码不能为空")
        sys.exit(1)

    if len(new_password) < 6:
        print("❌ 错误：密码长度至少 6 位")
        sys.exit(1)

    db = SessionLocal()
    try:
        # 查找 admin 用户
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            print("❌ 错误：未找到 admin 用户")
            print("   请先运行 init_admin.py 初始化管理员账号")
            sys.exit(1)

        # 更新密码
        admin.password_hash = get_password_hash(new_password)
        db.commit()

        print("✅ 管理员密码重置成功")
        print(f"   用户名: admin")
        print(f"   新密码: {new_password}")
        print(f"   ⚠️  请妥善保管密码")

    except Exception as e:
        db.rollback()
        print(f"❌ 重置失败: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python reset_admin_password.py <新密码>")
        print("示例: python reset_admin_password.py admin123")
        sys.exit(1)

    new_password = sys.argv[1]
    reset_admin_password(new_password)
