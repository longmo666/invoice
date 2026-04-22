"""
生成数据库迁移脚本
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_cleaning_task'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'cleaning_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('archive_type', sa.Enum('ZIP', '7Z', 'RAR', name='archivetype'), nullable=False),
        sa.Column('selected_types', sa.JSON(), nullable=False),
        sa.Column('status', sa.Enum('UPLOADING', 'PROCESSING', 'DONE', 'FAILED', name='cleaningstatus'), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('total_entries', sa.Integer(), nullable=False),
        sa.Column('matched_count', sa.Integer(), nullable=False),
        sa.Column('matched_by_type', sa.JSON(), nullable=True),
        sa.Column('skipped_count', sa.Integer(), nullable=False),
        sa.Column('failed_reason', sa.Text(), nullable=True),
        sa.Column('result_zip_path', sa.String(length=500), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cleaning_tasks_id'), 'cleaning_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_cleaning_tasks_user_id'), 'cleaning_tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_cleaning_tasks_status'), 'cleaning_tasks', ['status'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_cleaning_tasks_status'), table_name='cleaning_tasks')
    op.drop_index(op.f('ix_cleaning_tasks_user_id'), table_name='cleaning_tasks')
    op.drop_index(op.f('ix_cleaning_tasks_id'), table_name='cleaning_tasks')
    op.drop_table('cleaning_tasks')
