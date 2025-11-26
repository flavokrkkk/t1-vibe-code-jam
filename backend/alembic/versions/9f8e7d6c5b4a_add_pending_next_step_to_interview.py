"""add pending_next_step to interview

Revision ID: 9f8e7d6c5b4a
Revises: 8e7f6a5b4c3d
Create Date: 2025-11-26 02:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9f8e7d6c5b4a'
down_revision = '8e7f6a5b4c3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('interview', sa.Column('pending_next_step', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('interview', 'pending_next_step')


