"""empty message

Revision ID: de79b3cb9f73
Revises: daf94e37cb22
Create Date: 2019-01-12 04:18:17.478890

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'de79b3cb9f73'
down_revision = 'daf94e37cb22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('date_joined', sa.DateTime(), nullable=False))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'date_joined')
    # ### end Alembic commands ###
