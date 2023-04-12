"""empty message

Revision ID: feb3616914cf
Revises: 1d1ace56c9c2
Create Date: 2023-04-12 20:20:45.911129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'feb3616914cf'
down_revision = '1d1ace56c9c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('background', sa.String(length=400), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'background')
    # ### end Alembic commands ###