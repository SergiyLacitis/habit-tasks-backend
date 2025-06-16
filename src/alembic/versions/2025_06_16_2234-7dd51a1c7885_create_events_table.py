"""create events table

Revision ID: 7dd51a1c7885
Revises: ac9b35948ee6
Create Date: 2025-06-16 22:34:58.930437

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7dd51a1c7885"
down_revision: Union[str, None] = "ac9b35948ee6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "events",
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("friend_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["friend_id"], ["friends.id"], name=op.f("fk_events_friend_id_friends")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("events")
