"""
幂等 DDL 同步脚本 — 为 ai_config_test_runs 添加 status_code / diagnostic_steps 列
可重复执行，已存在则跳过。

用法: python scripts/sync_db_005.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "invoice.db")
DB_PATH = os.path.abspath(DB_PATH)

COLUMNS = [
    ("status_code", "INTEGER"),
    ("diagnostic_steps", "TEXT"),
]


def main():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取现有列
    cursor.execute("PRAGMA table_info(ai_config_test_runs)")
    existing = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in COLUMNS:
        if col_name in existing:
            print(f"  ✓ {col_name} 已存在，跳过")
        else:
            cursor.execute(f"ALTER TABLE ai_config_test_runs ADD COLUMN {col_name} {col_type}")
            print(f"  + {col_name} 已添加")

    conn.commit()
    conn.close()
    print("同步完成")


if __name__ == "__main__":
    main()
