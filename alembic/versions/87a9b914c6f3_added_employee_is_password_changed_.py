"""added employee.is_password_changed default=false

Revision ID: 87a9b914c6f3
Revises: 7bfcfe3616e0
Create Date: 2024-10-11 18:03:04.982732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87a9b914c6f3'
down_revision: Union[str, None] = '7bfcfe3616e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee', sa.Column('is_password_changed', sa.Boolean(), nullable=True))
    op.execute('UPDATE employee SET is_password_changed = false')
    op.alter_column('employee', 'is_password_changed', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('employee', 'is_password_changed')
    # ### end Alembic commands ###