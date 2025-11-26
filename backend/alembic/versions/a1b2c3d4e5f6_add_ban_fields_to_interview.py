"""add ban fields to interview

Revision ID: a1b2c3d4e5f6
Revises: 9f8e7d6c5b4a
Create Date: 2025-11-26 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9f8e7d6c5b4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новый статус BANNED в enum
    op.execute("ALTER TYPE interviewstatus ADD VALUE IF NOT EXISTS 'BANNED'")
    
    # Добавляем поля ban_reasons и banned_at
    op.add_column('interview', sa.Column('ban_reasons', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('interview', sa.Column('banned_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Удаляем добавленные поля
    op.drop_column('interview', 'banned_at')
    op.drop_column('interview', 'ban_reasons')
    
    # Примечание: удаление значения из enum в PostgreSQL сложнее и требует пересоздания типа
    # Для простоты оставляем статус BANNED в enum при откате

