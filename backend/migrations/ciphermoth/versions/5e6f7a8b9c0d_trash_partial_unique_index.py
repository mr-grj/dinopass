"""swap password_name unique constraint for a live-only partial index

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-07-21 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "5e6f7a8b9c0d"
down_revision = "4d5e6f7a8b9c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("passwords_password_name_key", "passwords", type_="unique")
    op.create_index(
        "uq_passwords_name_active",
        "passwords",
        ["password_name"],
        unique=True,
        postgresql_where=sa.text("deleted IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_passwords_name_active", table_name="passwords")
    op.create_unique_constraint(
        "passwords_password_name_key", "passwords", ["password_name"]
    )
