"""added tables inquiry and message

Revision ID: f5ed1f5c8a5f
Revises: ab2caa1b795f
Create Date: 2024-10-21 15:51:49.316774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5ed1f5c8a5f'
down_revision: Union[str, None] = 'ab2caa1b795f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inquiry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_inquiry_employee_id', 'inquiry', ['employee_id'], unique=False)
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inquiry_id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sent_at', sa.DateTime(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['inquiry_id'], ['inquiry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_message_inquiry_id', 'message', ['inquiry_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('users_unique_constraint', 'users', type_='unique')
    op.drop_index('idx_message_inquiry_id', table_name='message')
    op.drop_table('message')
    op.drop_index('idx_inquiry_employee_id', table_name='inquiry')
    op.drop_table('inquiry')
    # ### end Alembic commands ###