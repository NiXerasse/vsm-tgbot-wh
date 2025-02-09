"""added service record to subdivision

Revision ID: 5b1e444ed0fd
Revises: 4867173c022e
Create Date: 2024-10-23 13:57:19.357895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b1e444ed0fd'
down_revision: Union[str, None] = '4867173c022e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    # Check if the record already exists
    result = connection.execute(sa.text("SELECT id FROM subdivision WHERE name = '.service'"))
    exists = result.fetchone()

    # Insert the record if it doesn't exist
    if not exists:
        connection.execute(
            sa.text("INSERT INTO subdivision (name, created, updated) VALUES ('.service', now(), now())")
        )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM subdivision WHERE name = '.service'"))

