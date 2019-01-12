"""empty message

Revision ID: 51309767c82b
Revises: 16901c17e6e5
Create Date: 2019-01-11 18:58:06.608292

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '51309767c82b'
down_revision = '16901c17e6e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email', sqlalchemy_utils.types.email.EmailType(length=250), nullable=False))
    op.drop_constraint(u'user_username_key', 'user', type_='unique')
    op.create_unique_constraint(None, 'user', ['email'])
    op.drop_column('user', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', sa.VARCHAR(length=120), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user', type_='unique')
    op.create_unique_constraint(u'user_username_key', 'user', ['username'])
    op.drop_column('user', 'email')
    # ### end Alembic commands ###
