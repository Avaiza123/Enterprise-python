"""initial

Revision ID: 0001
Revises:
Create Date: 2026-01-01
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "items",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table("items")
