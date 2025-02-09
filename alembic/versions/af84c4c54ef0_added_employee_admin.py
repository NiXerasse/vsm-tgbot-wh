"""added employee_admin

Revision ID: af84c4c54ef0
Revises: 8afd0532ca61
Create Date: 2024-10-24 15:29:39.999239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af84c4c54ef0'
down_revision: Union[str, None] = '8afd0532ca61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee_admin',
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
    sa.PrimaryKeyConstraint('employee_id'),
    sa.UniqueConstraint('employee_id', name='uq_employee_admin')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('employee_admin')
    # ### end Alembic commands ###
