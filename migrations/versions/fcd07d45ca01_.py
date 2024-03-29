"""empty message

Revision ID: fcd07d45ca01
Revises: 2fd5a06e09b0
Create Date: 2019-01-11 05:39:20.505585

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'fcd07d45ca01'
down_revision = '2fd5a06e09b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('updates_log', sa.Column('task_id', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('updates_log', 'task_id')
    # ### end Alembic commands ###
