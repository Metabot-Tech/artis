"""Add balances table

Revision ID: bbebd125c978
Revises: b9765b41dd10
Create Date: 2017-12-29 20:02:38.763275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbebd125c978'
down_revision = 'b9765b41dd10'
branch_labels = None
depends_on = 'd5d9b1f37711'


def upgrade():
    op.create_table('balances',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('transaction_id', sa.Integer, sa.ForeignKey("transactions.id"), nullable=True),
                    sa.Column('created', sa.DateTime, nullable=False),
                    sa.Column('market', sa.String, nullable=False),
                    sa.Column('coin', sa.String, nullable=False),
                    sa.Column('amount', sa.Numeric(25, 18), nullable=False))


def downgrade():
    op.drop_table('balances')
