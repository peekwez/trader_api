"""empty message

Revision ID: ec9572d3273c
Revises:
Create Date: 2019-01-04 14:52:11.816990

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from models import Ticker

# revision identifiers, used by Alembic.
revision = 'ec9572d3273c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tickers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('symbol', sa.String(length=50), nullable=False),
    sa.Column('sector', sa.String(length=250), nullable=True),
    sa.Column('industry', sa.String(length=250), nullable=True),
    sa.Column('market', sqlalchemy_utils.types.choice.ChoiceType(Ticker.MARKETS), nullable=False),
    sa.Column('type', sqlalchemy_utils.types.choice.ChoiceType(Ticker.TYPES), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('symbol')
    )
    op.create_table('prices',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ticker_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('open', sa.Float(), nullable=False),
    sa.Column('low', sa.Float(), nullable=False),
    sa.Column('high', sa.Float(), nullable=False),
    sa.Column('close', sa.Float(), nullable=False),
    sa.Column('adj_close', sa.Float(), nullable=False),
    sa.Column('volume', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['ticker_id'], ['tickers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prices')
    op.drop_table('tickers')
    # ### end Alembic commands ###
