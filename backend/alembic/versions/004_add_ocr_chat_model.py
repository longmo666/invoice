"""add ocr_chat_model to ai_configs

Revision ID: 004
Revises: 003
Create Date: 2026-04-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    """检查列是否已存在（兼容 SQLite / PostgreSQL / MySQL）"""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if not _column_exists("ai_configs", "ocr_chat_model"):
        op.add_column(
            'ai_configs',
            sa.Column('ocr_chat_model', sa.String(100), nullable=True,
                       comment='OCR 模式下结构化提取用的 chat 模型')
        )


def downgrade() -> None:
    if _column_exists("ai_configs", "ocr_chat_model"):
        op.drop_column('ai_configs', 'ocr_chat_model')
