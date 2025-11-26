"""remove ml_requirements from interviewstep

Revision ID: 8e7f6a5b4c3d
Revises: 7d6e5f4a3b2c
Create Date: 2025-11-26 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8e7f6a5b4c3d'
down_revision = '7d6e5f4a3b2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('interviewstep', 'ml_requirements')


def downgrade() -> None:
    op.add_column('interviewstep', sa.Column('ml_requirements', sa.JSON(), nullable=True))


