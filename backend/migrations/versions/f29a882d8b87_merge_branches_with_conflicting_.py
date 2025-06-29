"""Merge branches with conflicting migrations

Revision ID: f29a882d8b87
Revises: 37c8d99e39f4, 51c8e290b8c8
Create Date: 2025-06-29 21:22:03.051924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f29a882d8b87'
down_revision = ('37c8d99e39f4', '51c8e290b8c8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
