"""create word table

Revision ID: 98227d5c2e56
Revises: 5488bdeceba6
Create Date: 2021-02-26 15:50:43.187882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98227d5c2e56'
down_revision = '5488bdeceba6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('word',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('origin', sa.String(), nullable=False),
    sa.Column('pronunciation', sa.String(), nullable=True),
    sa.Column('translation', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_word_id'), 'word', ['id'], unique=False)
    op.create_index(op.f('ix_word_origin'), 'word', ['origin'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_word_origin'), table_name='word')
    op.drop_index(op.f('ix_word_id'), table_name='word')
    op.drop_table('word')
    # ### end Alembic commands ###
