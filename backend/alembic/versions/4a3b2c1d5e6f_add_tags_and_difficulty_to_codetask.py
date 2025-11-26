"""add tags, difficulty, topic to codetask

Revision ID: 4a3b2c1d5e6f
Revises: 29c45779f221
Create Date: 2025-11-26 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4a3b2c1d5e6f'
down_revision = '29c45779f221'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('codetask', sa.Column('tags', sa.JSON(), server_default='[]', nullable=False))
    op.add_column('codetask', sa.Column('difficulty', sa.String(), server_default='medium', nullable=False))
    op.add_column('codetask', sa.Column('topic', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('codetask', 'topic')
    op.drop_column('codetask', 'difficulty')
    op.drop_column('codetask', 'tags')
