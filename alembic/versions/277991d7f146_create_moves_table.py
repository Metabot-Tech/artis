"""Create moves table

Revision ID: 277991d7f146
Revises: d5d9b1f37711
Create Date: 2017-12-23 15:16:38.685676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '277991d7f146'
down_revision = 'd5d9b1f37711'
branch_labels = None
depends_on = 'd5d9b1f37711'


def upgrade():
    op.create_table('moves',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('transaction', sa.Integer, sa.ForeignKey("transactions.id"), nullable=False),
                    sa.Column('created', sa.DateTime, server_default=sa.func.current_timestamp()),
                    sa.Column('updated', sa.DateTime, server_default=sa.func.current_timestamp(),
                              server_onupdate=sa.func.current_timestamp()),
                    sa.Column('origin', sa.String, nullable=False),
                    sa.Column('destination', sa.String, nullable=False),
                    sa.Column('amount', sa.Numeric(25, 18), server_default='0.0'),
                    sa.Column('coin', sa.String, nullable=False),
                    sa.Column('status', sa.String),
                    sa.Column('error', sa.String))


def downgrade():
    op.drop_table('moves')
