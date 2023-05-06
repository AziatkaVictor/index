"""empty message

Revision ID: df5b3d5dd331
Revises: bcca33c2b4ce
Create Date: 2023-05-04 16:38:13.180449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df5b3d5dd331'
down_revision = 'bcca33c2b4ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('сomplaint', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_сomplaint_status'), ['status'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_сomplaint_status_complaint_status'), 'complaint_status', ['status'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('сomplaint', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_сomplaint_status_complaint_status'), type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_сomplaint_status'))
        batch_op.drop_column('status')

    # ### end Alembic commands ###