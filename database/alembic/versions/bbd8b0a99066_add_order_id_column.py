"""Add order_id column

Revision ID: bbd8b0a99066
Revises: b9765b41dd10
Create Date: 2017-12-24 16:02:59.404848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbd8b0a99066'
down_revision = 'b9765b41dd10'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('trades',
                  sa.Column("order_id", sa.Integer, nullable=False))


def downgrade():
    op.drop_column('trades', "order_id")
