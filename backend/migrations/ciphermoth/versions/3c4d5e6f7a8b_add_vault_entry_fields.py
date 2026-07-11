"""add url, totp, tags, history and favorite to passwords

Revision ID: 3c4d5e6f7a8b
Revises: 2a3b4c5d6e7f
Create Date: 2026-07-09 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "3c4d5e6f7a8b"
down_revision = "2a3b4c5d6e7f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("passwords", sa.Column("url", sa.LargeBinary(), nullable=True))
    op.add_column(
        "passwords", sa.Column("totp_secret", sa.LargeBinary(), nullable=True)
    )
    op.add_column("passwords", sa.Column("tags", sa.LargeBinary(), nullable=True))
    op.add_column(
        "passwords", sa.Column("password_history", sa.LargeBinary(), nullable=True)
    )
    op.add_column(
        "passwords",
        sa.Column(
            "favorite",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("passwords", "favorite")
    op.drop_column("passwords", "password_history")
    op.drop_column("passwords", "tags")
    op.drop_column("passwords", "totp_secret")
    op.drop_column("passwords", "url")
