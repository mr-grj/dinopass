"""initial

Revision ID: 1b3a2c4d5e6f
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "1b3a2c4d5e6f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "master_password",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted", sa.TIMESTAMP(), nullable=True),
        sa.Column("salt", sa.LargeBinary(), nullable=False),
        sa.Column("hash_key", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "passwords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted", sa.TIMESTAMP(), nullable=True),
        sa.Column("password_name", sa.String(), nullable=False),
        sa.Column("password_value", sa.LargeBinary(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "backed_up",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("password_name"),
    )
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "inactivity_ms", sa.Integer(), server_default="120000", nullable=False
        ),
        sa.Column(
            "warn_before_ms", sa.Integer(), server_default="60000", nullable=False
        ),
        sa.Column("hidden_ms", sa.Integer(), server_default="60000", nullable=False),
        sa.Column("debounce_ms", sa.Integer(), server_default="1000", nullable=False),
        sa.Column(
            "clipboard_clear_ms", sa.Integer(), server_default="30000", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("settings")
    op.drop_table("passwords")
    op.drop_table("master_password")
