"""add encrypted folder to passwords

Revision ID: 7a8b9c0d1e2f
Revises: 6f7a8b9c0d1e
Create Date: 2026-07-21 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "7a8b9c0d1e2f"
down_revision = "6f7a8b9c0d1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("passwords", sa.Column("folder", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("passwords", "folder")
