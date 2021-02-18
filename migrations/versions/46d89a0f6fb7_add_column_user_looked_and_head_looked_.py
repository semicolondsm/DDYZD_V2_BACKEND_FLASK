"""add column user_looked and head_looked in table Room

Revision ID: 46d89a0f6fb7
Revises: 559791afab6a
Create Date: 2021-02-18 19:50:57.907924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46d89a0f6fb7'
down_revision = '559791afab6a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('room', 'looked')
    op.add_column('room', sa.Column('user_looked', sa.Boolean(), nullable=False))
    op.add_column('room', sa.Column('head_looked', sa.Boolean(), nullable=False))
    pass


def downgrade():
    op.add_column('room', sa.Column('looked', sa.Boolean(), nullable=False))
    pass
