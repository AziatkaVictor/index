"""empty message

Revision ID: 0891e12f7c3f
Revises: 0af2e45a58bb
Create Date: 2023-04-13 19:29:06.983422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0891e12f7c3f'
down_revision = '0af2e45a58bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('age', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'age')
    # ### end Alembic commands ###