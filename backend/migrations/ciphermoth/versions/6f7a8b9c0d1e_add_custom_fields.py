"""add encrypted custom_fields to passwords

Revision ID: 6f7a8b9c0d1e
Revises: 5e6f7a8b9c0d
Create Date: 2026-07-21 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "6f7a8b9c0d1e"
down_revision = "5e6f7a8b9c0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "passwords", sa.Column("custom_fields", sa.LargeBinary(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("passwords", "custom_fields")
