"""add kdf_version to master_password

Revision ID: 3f4a5b6c7d8e
Revises: 1b3a2c4d5e6f
Create Date: 2026-03-14 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "3f4a5b6c7d8e"
down_revision = "1b3a2c4d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "master_password",
        sa.Column(
            "kdf_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )


def downgrade() -> None:
    op.drop_column("master_password", "kdf_version")
