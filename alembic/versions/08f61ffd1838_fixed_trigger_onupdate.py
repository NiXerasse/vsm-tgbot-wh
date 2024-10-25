"""fixed trigger onupdate

Revision ID: 08f61ffd1838
Revises: af84c4c54ef0
Create Date: 2024-10-25 11:44:12.047111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08f61ffd1838'
down_revision: Union[str, None] = 'af84c4c54ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_column()
        RETURNS TRIGGER AS $$
        BEGIN
           NEW.updated = NOW();
           RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

    op.execute("""
        CREATE TRIGGER set_updated_timestamp
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_column();
        """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_updated_timestamp ON users;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_column;")
