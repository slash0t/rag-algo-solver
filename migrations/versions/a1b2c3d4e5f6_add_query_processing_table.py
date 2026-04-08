"""add query_processing table and make queries.user_id nullable

Revision ID: a1b2c3d4e5f6
Revises: dce56e4c70b2
Create Date: 2026-04-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "dce56e4c70b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "queries",
        "user_id",
        existing_type=sa.Uuid(),
        nullable=True,
    )

    op.create_table(
        "query_processing",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "query_id",
            sa.Uuid(),
            sa.ForeignKey("queries.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("enriched_text", sa.Text(), nullable=True),
        sa.Column("task_context", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("query_processing")

    op.alter_column(
        "queries",
        "user_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )
