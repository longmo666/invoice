"""
生成识别相关表的数据库迁移脚本
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_recognition_tables'
down_revision = 'add_cleaning_task'
branch_labels = None
depends_on = None

def upgrade():
    # 创建 ai_configs 表
    op.create_table(
        'ai_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='配置名称'),
        sa.Column('provider_type', sa.String(length=50), nullable=False, comment='提供商类型: openai_compatible, anthropic_compatible'),
        sa.Column('base_url', sa.String(length=500), nullable=False, comment='API 基础 URL'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('api_key', sa.Text(), nullable=False, comment='API 密钥'),
        sa.Column('timeout', sa.Integer(), nullable=True, comment='超时时间（秒）'),
        sa.Column('temperature', sa.Float(), nullable=True, comment='温度参数'),
        sa.Column('max_tokens', sa.Integer(), nullable=True, comment='最大 token 数'),
        sa.Column('max_concurrency', sa.Integer(), nullable=False, comment='最大并发数（1 表示串行）'),
        sa.Column('enabled', sa.Boolean(), nullable=False, comment='是否启用'),
        sa.Column('active', sa.Boolean(), nullable=False, comment='是否激活（只能有一个激活）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='软删除时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_configs_id'), 'ai_configs', ['id'], unique=False)

    # 创建 recognition_tasks 表
    op.create_table(
        'recognition_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户 ID'),
        sa.Column('original_filename', sa.String(length=500), nullable=False, comment='原始文件名'),
        sa.Column('file_type', sa.Enum('IMAGE', 'PDF', 'XML', 'OFD', name='filetype'), nullable=False, comment='文件类型'),
        sa.Column('file_path', sa.String(length=1000), nullable=False, comment='文件存储路径'),
        sa.Column('file_size', sa.Integer(), nullable=False, comment='文件大小（字节）'),
        sa.Column('invoice_type', sa.Enum('VAT_SPECIAL', 'VAT_NORMAL', 'RAILWAY_TICKET', name='invoicetype'), nullable=False, comment='发票类型'),
        sa.Column('recognition_mode', sa.Enum('LOCAL_OCR', 'AI', 'HYBRID', name='recognitionmode'), nullable=False, comment='识别模式'),
        sa.Column('ai_config_id', sa.Integer(), nullable=True, comment='使用的 AI 配置 ID'),
        sa.Column('status', sa.Enum('UPLOADING', 'PROCESSING', 'DONE', 'FAILED', name='taskstatus'), nullable=False, comment='任务状态'),
        sa.Column('progress', sa.Integer(), nullable=True, comment='进度百分比 0-100'),
        sa.Column('total_items', sa.Integer(), nullable=True, comment='识别出的总项数'),
        sa.Column('success_items', sa.Integer(), nullable=True, comment='成功项数'),
        sa.Column('failed_items', sa.Integer(), nullable=True, comment='失败项数'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='软删除时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ai_config_id'], ['ai_configs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recognition_tasks_id'), 'recognition_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_recognition_tasks_user_id'), 'recognition_tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_recognition_tasks_status'), 'recognition_tasks', ['status'], unique=False)
    op.create_index(op.f('ix_recognition_tasks_created_at'), 'recognition_tasks', ['created_at'], unique=False)

    # 创建 recognition_items 表
    op.create_table(
        'recognition_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False, comment='所属任务 ID'),
        sa.Column('page_number', sa.Integer(), nullable=True, comment='页码（PDF 多页时使用）'),
        sa.Column('item_index', sa.Integer(), nullable=False, comment='在任务中的索引（从 0 开始）'),
        sa.Column('raw_response', sa.JSON(), nullable=True, comment='AI 原始响应'),
        sa.Column('original_result', sa.JSON(), nullable=False, comment='结构化的原始识别结果'),
        sa.Column('reviewed_result', sa.JSON(), nullable=False, comment='复核后的结果'),
        sa.Column('review_status', sa.Enum('AUTO_PASSED', 'PENDING_REVIEW', 'MANUAL_CONFIRMED', name='reviewstatus'), nullable=False, comment='复核状态'),
        sa.Column('review_reason', sa.String(length=500), nullable=True, comment='待复核原因'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True, comment='复核人 ID'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True, comment='复核时间'),
        sa.Column('confidence_score', sa.Numeric(precision=3, scale=2), nullable=True, comment='置信度分数'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='软删除时间'),
        sa.ForeignKeyConstraint(['task_id'], ['recognition_tasks.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recognition_items_id'), 'recognition_items', ['id'], unique=False)
    op.create_index(op.f('ix_recognition_items_task_id'), 'recognition_items', ['task_id'], unique=False)
    op.create_index(op.f('ix_recognition_items_review_status'), 'recognition_items', ['review_status'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_recognition_items_review_status'), table_name='recognition_items')
    op.drop_index(op.f('ix_recognition_items_task_id'), table_name='recognition_items')
    op.drop_index(op.f('ix_recognition_items_id'), table_name='recognition_items')
    op.drop_table('recognition_items')

    op.drop_index(op.f('ix_recognition_tasks_created_at'), table_name='recognition_tasks')
    op.drop_index(op.f('ix_recognition_tasks_status'), table_name='recognition_tasks')
    op.drop_index(op.f('ix_recognition_tasks_user_id'), table_name='recognition_tasks')
    op.drop_index(op.f('ix_recognition_tasks_id'), table_name='recognition_tasks')
    op.drop_table('recognition_tasks')

    op.drop_index(op.f('ix_ai_configs_id'), table_name='ai_configs')
    op.drop_table('ai_configs')
