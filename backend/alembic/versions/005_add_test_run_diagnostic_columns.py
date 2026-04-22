"""add status_code and diagnostic_steps to ai_config_test_runs

Revision ID: 005
Revises: 004
Create Date: 2026-04-21
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    """检查列是否已存在（兼容 SQLite / PostgreSQL / MySQL）"""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if not _column_exists("ai_config_test_runs", "status_code"):
        op.add_column("ai_config_test_runs", sa.Column("status_code", sa.Integer(), nullable=True, comment="HTTP 状态码"))
    if not _column_exists("ai_config_test_runs", "diagnostic_steps"):
        op.add_column("ai_config_test_runs", sa.Column("diagnostic_steps", sa.Text(), nullable=True, comment="诊断步骤（JSON）"))


def downgrade() -> None:
    if _column_exists("ai_config_test_runs", "diagnostic_steps"):
        op.drop_column("ai_config_test_runs", "diagnostic_steps")
    if _column_exists("ai_config_test_runs", "status_code"):
        op.drop_column("ai_config_test_runs", "status_code")
