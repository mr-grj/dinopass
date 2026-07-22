"""add password_attachments table

Revision ID: 9c0d1e2f3a4b
Revises: 8b9c0d1e2f3a
Create Date: 2026-07-22 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "9c0d1e2f3a4b"
down_revision = "8b9c0d1e2f3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.TIMESTAMP(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("password_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.LargeBinary(), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("content_type", sa.LargeBinary(), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["password_id"], ["passwords.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_password_attachments_password_id",
        "password_attachments",
        ["password_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_password_attachments_password_id",
        table_name="password_attachments",
    )
    op.drop_table("password_attachments")
