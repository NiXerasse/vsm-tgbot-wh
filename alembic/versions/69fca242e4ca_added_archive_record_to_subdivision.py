"""added .archive record to subdivision

Revision ID: 69fca242e4ca
Revises: 5b1e444ed0fd
Create Date: 2024-10-23 16:35:19.526707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69fca242e4ca'
down_revision: Union[str, None] = '5b1e444ed0fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    # Check if the record already exists
    result = connection.execute(sa.text("SELECT id FROM subdivision WHERE name = '.archive'"))
    exists = result.fetchone()

    # Insert the record if it doesn't exist
    if not exists:
        connection.execute(
            sa.text("INSERT INTO subdivision (name, created, updated) VALUES ('.archive', now(), now())")
        )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM subdivision WHERE name = '.archive'"))

