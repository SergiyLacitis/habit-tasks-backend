"""added password column for User model

Revision ID: b4c568566a96
Revises: 7dd51a1c7885
Create Date: 2025-09-03 19:46:40.022912

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4c568566a96"
down_revision: Union[str, None] = "7dd51a1c7885"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("password", sa.String(length=128), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password")
