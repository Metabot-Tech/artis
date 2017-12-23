"""Create transactions table

Revision ID: d5d9b1f37711
Revises: 
Create Date: 2017-12-23 14:02:38.281049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5d9b1f37711'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('transactions',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('created', sa.DateTime, server_default=sa.func.current_timestamp()),
                    sa.Column('updated', sa.DateTime, server_default=sa.func.current_timestamp(),
                              server_onupdate=sa.func.current_timestamp()),
                    sa.Column('profit', sa.Numeric(25, 18), server_default='0.0'),
                    sa.Column('status', sa.String),
                    sa.Column('error', sa.String))


def downgrade():
    op.drop_table('transactions')
