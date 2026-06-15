from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel

if TYPE_CHECKING:
    from sbtb.models import Fighter


class FeaturedCollection(StrEnum):
    popular_fighters = "popular_fighters"


class FeaturedFighter(RecordModel):
    __tablename__ = "featured_fighters"

    fighter_id: Mapped[UUID] = mapped_column(ForeignKey("fighters.id", ondelete="CASCADE"), nullable=False)
    collection: Mapped[FeaturedCollection] = mapped_column(
        ENUM(FeaturedCollection, name="featuredcollection", create_type=True),
        nullable=False,
        index=True,
    )
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    fighter: Mapped["Fighter"] = relationship("Fighter")

    __table_args__ = (
        # A fighter can be in multiple collections but only once per collection
        UniqueConstraint("collection", "fighter_id", name="uq_featured_collection_fighter"),
        # Within a collection, no two fighters share the same non-null position
        Index(
            "uq_featured_collection_position",
            "collection",
            "position",
            unique=True,
            postgresql_where=text("position IS NOT NULL"),
        ),
    )
