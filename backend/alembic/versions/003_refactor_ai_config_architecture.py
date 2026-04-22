"""refactor ai config architecture

Revision ID: 003
Revises: 002
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 添加新字段
    op.add_column('ai_configs', sa.Column('provider_vendor', sa.String(50), nullable=True, comment='提供商厂商: openai_compatible, anthropic_compatible'))
    op.add_column('ai_configs', sa.Column('api_style', sa.String(50), nullable=True, comment='API 风格: openai_responses, openai_chat_completions, anthropic_messages'))
    op.add_column('ai_configs', sa.Column('supports_image_input', sa.Boolean(), default=True, nullable=False, comment='是否支持图片输入'))
    op.add_column('ai_configs', sa.Column('supports_pdf_file_input', sa.Boolean(), default=False, nullable=False, comment='是否支持 PDF 文件输入'))
    op.add_column('ai_configs', sa.Column('supports_file_id', sa.Boolean(), default=False, nullable=False, comment='是否支持文件 ID'))
    op.add_column('ai_configs', sa.Column('supports_file_url', sa.Boolean(), default=False, nullable=False, comment='是否支持文件 URL'))
    op.add_column('ai_configs', sa.Column('requires_files_api', sa.Boolean(), default=False, nullable=False, comment='是否需要先调用 files API'))
    op.add_column('ai_configs', sa.Column('supports_structured_json', sa.Boolean(), default=False, nullable=False, comment='是否支持结构化 JSON 输出'))

    # 2. 迁移现有数据：将 provider_type 拆分为 provider_vendor 和 api_style
    # openai_compatible -> provider_vendor=openai_compatible, api_style=openai_chat_completions
    # anthropic_compatible -> provider_vendor=anthropic_compatible, api_style=anthropic_messages
    op.execute("""
        UPDATE ai_configs
        SET provider_vendor = 'openai_compatible',
            api_style = 'openai_chat_completions',
            supports_image_input = true,
            supports_pdf_file_input = false,
            supports_file_id = false,
            supports_file_url = false,
            requires_files_api = false,
            supports_structured_json = true
        WHERE provider_type = 'openai_compatible'
    """)

    op.execute("""
        UPDATE ai_configs
        SET provider_vendor = 'anthropic_compatible',
            api_style = 'anthropic_messages',
            supports_image_input = true,
            supports_pdf_file_input = true,
            supports_file_id = false,
            supports_file_url = false,
            requires_files_api = false,
            supports_structured_json = false
        WHERE provider_type = 'anthropic_compatible'
    """)

    # 3. 设置新字段为 NOT NULL
    op.alter_column('ai_configs', 'provider_vendor', nullable=False)
    op.alter_column('ai_configs', 'api_style', nullable=False)

    # 4. 删除旧字段
    op.drop_column('ai_configs', 'provider_type')


def downgrade() -> None:
    # 1. 恢复旧字段
    op.add_column('ai_configs', sa.Column('provider_type', sa.String(50), nullable=True, comment='提供商类型: openai_compatible, anthropic_compatible'))

    # 2. 迁移数据回去
    op.execute("""
        UPDATE ai_configs
        SET provider_type = provider_vendor
    """)

    op.alter_column('ai_configs', 'provider_type', nullable=False)

    # 3. 删除新字段
    op.drop_column('ai_configs', 'provider_vendor')
    op.drop_column('ai_configs', 'api_style')
    op.drop_column('ai_configs', 'supports_image_input')
    op.drop_column('ai_configs', 'supports_pdf_file_input')
    op.drop_column('ai_configs', 'supports_file_id')
    op.drop_column('ai_configs', 'supports_file_url')
    op.drop_column('ai_configs', 'requires_files_api')
    op.drop_column('ai_configs', 'supports_structured_json')
