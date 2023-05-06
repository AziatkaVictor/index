"""empty message

Revision ID: bcca33c2b4ce
Revises: dcd71198d0c8
Create Date: 2023-05-04 16:34:46.487467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcca33c2b4ce'
down_revision = 'dcd71198d0c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_user_email'), ['email'])
        batch_op.create_unique_constraint(batch_op.f('uq_user_id'), ['id'])
        batch_op.create_unique_constraint(batch_op.f('uq_user_username'), ['username'])

    with op.batch_alter_table('сomplaint', schema=None) as batch_op:
        batch_op.drop_index('ix_сomplaint_status')
        batch_op.drop_column('status')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('сomplaint', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.INTEGER(), nullable=True))
        batch_op.create_index('ix_сomplaint_status', ['status'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_user_username'), type_='unique')
        batch_op.drop_constraint(batch_op.f('uq_user_id'), type_='unique')
        batch_op.drop_constraint(batch_op.f('uq_user_email'), type_='unique')

    # ### end Alembic commands ###
