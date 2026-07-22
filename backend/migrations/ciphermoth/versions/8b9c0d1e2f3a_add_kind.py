"""add kind discriminator to passwords

Revision ID: 8b9c0d1e2f3a
Revises: 7a8b9c0d1e2f
Create Date: 2026-07-22 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "8b9c0d1e2f3a"
down_revision = "7a8b9c0d1e2f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "passwords",
        sa.Column(
            "kind",
            sa.String(),
            nullable=False,
            server_default="login",
        ),
    )


def downgrade() -> None:
    op.drop_column("passwords", "kind")
