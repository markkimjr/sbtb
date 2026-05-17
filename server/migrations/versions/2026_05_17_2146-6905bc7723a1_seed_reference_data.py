"""seed reference data

Revision ID: 6905bc7723a1
Revises: c435cee8315e
Create Date: 2026-05-17 21:46:40.437153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6905bc7723a1'
down_revision: Union[str, None] = 'c435cee8315e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BOXING_ORGANIZATIONS = ["IBF", "WBA", "WBC", "WBO"]

# (name, pounds) — heavyweight has no upper limit so pounds is NULL
WEIGHT_CLASSES = [
    ("heavyweight", None),
    ("cruiserweight", 200),
    ("light heavyweight", 175),
    ("super middleweight", 168),
    ("middleweight", 160),
    ("junior middleweight", 154),
    ("welterweight", 147),
    ("junior welterweight", 140),
    ("lightweight", 135),
    ("junior lightweight", 130),
    ("featherweight", 126),
    ("junior featherweight", 122),
    ("bantamweight", 118),
    ("junior bantamweight", 115),
    ("flyweight", 112),
    ("junior flyweight", 108),
    ("strawweight", 105),
]


def upgrade() -> None:
    """Seed boxing organizations and weight classes."""
    for name in BOXING_ORGANIZATIONS:
        op.execute(
            f"INSERT INTO fight_organizations (id, name, sport, created_at) "
            f"VALUES (gen_random_uuid(), '{name}', 'boxing', NOW()) "
            f"ON CONFLICT (name) DO NOTHING"
        )

    for name, pounds in WEIGHT_CLASSES:
        pounds_value = str(pounds) if pounds is not None else "NULL"
        op.execute(
            f"INSERT INTO weight_classes (id, name, pounds, created_at) "
            f"VALUES (gen_random_uuid(), '{name}', {pounds_value}, NOW()) "
            f"ON CONFLICT (name) DO NOTHING"
        )


def downgrade() -> None:
    """Remove seeded reference data."""
    org_names = ", ".join(f"'{name}'" for name in BOXING_ORGANIZATIONS)
    op.execute(f"DELETE FROM fight_organizations WHERE name IN ({org_names})")

    weight_class_names = ", ".join(f"'{name}'" for name, _ in WEIGHT_CLASSES)
    op.execute(f"DELETE FROM weight_classes WHERE name IN ({weight_class_names})")
