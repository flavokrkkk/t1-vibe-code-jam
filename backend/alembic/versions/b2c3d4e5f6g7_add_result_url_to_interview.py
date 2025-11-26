"""add result_url to interview

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-26 21:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле result_url
    op.add_column('interview', sa.Column('result_url', sa.String(), nullable=True))


def downgrade() -> None:
    # Удаляем поле result_url
    op.drop_column('interview', 'result_url')

