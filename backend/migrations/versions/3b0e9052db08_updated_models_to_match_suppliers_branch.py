"""Updated models to match suppliers branch

Revision ID: 3b0e9052db08
Revises: d37a7cb191d3
Create Date: 2025-06-28 23:58:17.253239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b0e9052db08'
down_revision = 'd37a7cb191d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stock_transfers', schema=None) as batch_op:
        batch_op.alter_column('is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('0'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stock_transfers', schema=None) as batch_op:
        batch_op.alter_column('is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('0'))

    # ### end Alembic commands ###
