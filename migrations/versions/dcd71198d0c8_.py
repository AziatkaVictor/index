"""empty message

Revision ID: dcd71198d0c8
Revises: 0891e12f7c3f
Create Date: 2023-05-04 15:35:48.330403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcd71198d0c8'
down_revision = '0891e12f7c3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('complaint_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['rule.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rule_parent_id'), 'rule', ['parent_id'], unique=False)
    op.create_table('сomplaint',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rules', sa.String(), nullable=True),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('сomplaint')
    op.drop_index(op.f('ix_rule_parent_id'), table_name='rule')
    op.drop_table('rule')
    op.drop_table('complaint_status')
    # ### end Alembic commands ###