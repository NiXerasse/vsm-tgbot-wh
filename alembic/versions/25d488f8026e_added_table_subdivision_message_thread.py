"""added table subdivision_message_thread

Revision ID: 25d488f8026e
Revises: f5ed1f5c8a5f
Create Date: 2024-10-22 17:28:02.074421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25d488f8026e'
down_revision: Union[str, None] = 'f5ed1f5c8a5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subdivision_message_thread',
    sa.Column('subdivision_id', sa.Integer(), nullable=False),
    sa.Column('message_thread_id', sa.BigInteger(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['subdivision_id'], ['subdivision.id'], ),
    sa.PrimaryKeyConstraint('subdivision_id'),
    sa.UniqueConstraint('subdivision_id', 'message_thread_id', name='uq_subdivision_message_thread')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subdivision_message_thread')
    # ### end Alembic commands ###