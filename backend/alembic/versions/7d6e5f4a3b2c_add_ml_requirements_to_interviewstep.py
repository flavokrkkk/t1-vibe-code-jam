"""add ml_requirements to interviewstep

Revision ID: 7d6e5f4a3b2c
Revises: 4a3b2c1d5e6f
Create Date: 2025-11-26 01:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7d6e5f4a3b2c'
down_revision = '4a3b2c1d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('interviewstep', sa.Column('ml_requirements', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('interviewstep', 'ml_requirements')


