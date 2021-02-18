"""add column looked to tables rooms

Revision ID: 559791afab6a
Revises: f71d402e05f6
Create Date: 2021-02-17 20:14:29.440129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '559791afab6a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('room', sa.Column('looked', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('room', 'looked')
