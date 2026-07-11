"""add username to passwords

Revision ID: 2a3b4c5d6e7f
Revises: 1b3a2c4d5e6f
Create Date: 2026-03-15 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "2a3b4c5d6e7f"
down_revision = "1b3a2c4d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("passwords", sa.Column("username", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("passwords", "username")
