"""Create trades table

Revision ID: b9765b41dd10
Revises: 277991d7f146
Create Date: 2017-12-23 15:31:42.775546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9765b41dd10'
down_revision = '277991d7f146'
branch_labels = None
depends_on = 'd5d9b1f37711'


def upgrade():
    op.create_table('trades',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('transaction_id', sa.Integer, sa.ForeignKey("transactions.id"), nullable=False),
                    sa.Column("order_id", sa.Integer),
                    sa.Column('created', sa.DateTime, nullable=False),
                    sa.Column('updated', sa.DateTime, nullable=False),
                    sa.Column('market', sa.String, nullable=False),
                    sa.Column('type', sa.String, nullable=False),
                    sa.Column('coin', sa.String, nullable=False),
                    sa.Column('amount', sa.Numeric(25, 18), nullable=False),
                    sa.Column('price', sa.Numeric(25, 18), nullable=False),
                    sa.Column('status', sa.String, nullable=False),
                    sa.Column('error', sa.String))


def downgrade():
    op.drop_table('trades')
