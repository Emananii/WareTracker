"""Remove stock_level column from Product

Revision ID: 51c8e290b8c8
Revises: b7ed53260db9
Create Date: 2025-06-29 15:16:05.095747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51c8e290b8c8'
down_revision = 'b7ed53260db9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('stock_level')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stock_level', sa.INTEGER(), server_default=sa.text('0'), nullable=False))

    # ### end Alembic commands ###
