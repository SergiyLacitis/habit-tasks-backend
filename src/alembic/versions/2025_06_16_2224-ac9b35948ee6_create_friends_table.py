"""create friends table

Revision ID: ac9b35948ee6
Revises: 833cf6c389ff
Create Date: 2025-06-16 22:24:13.152376

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ac9b35948ee6"
down_revision: Union[str, None] = "833cf6c389ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "friends",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("birdthDay", sa.String(), nullable=False),
        sa.Column("is_favority", sa.Boolean(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_friends_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_friends")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("friends")
