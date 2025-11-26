"""add usage_count to codetask

Revision ID: 29c45779f221
Revises: e5dc874670fd
Create Date: 2025-11-26 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '29c45779f221'
down_revision = 'e5dc874670fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('codetask', sa.Column('usage_count', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('codetask', 'usage_count')


