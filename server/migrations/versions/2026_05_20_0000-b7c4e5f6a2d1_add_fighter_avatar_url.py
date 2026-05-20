"""add fighter avatar_url

Revision ID: b7c4e5f6a2d1
Revises: f3a8d2c1b4e9
Create Date: 2026-05-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c4e5f6a2d1"
down_revision: Union[str, None] = "f3a8d2c1b4e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("fighters", sa.Column("avatar_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("fighters", "avatar_url")