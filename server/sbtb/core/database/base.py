from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, MetaData, Uuid, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sbtb.core.util import utc_now

my_metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_N_label)s",
        "uq": "%(table_name)s_%(column_0_N_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
        "pk": "%(table_name)s_pkey",
    }
)


class BaseModel(DeclarativeBase):
    __abstract__ = True

    metadata = my_metadata


class TimestampedModel(BaseModel):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=utc_now, index=True
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=utc_now,
        nullable=True,
        default=None,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )

    def set_modified_at(self) -> None:
        self.modified_at = utc_now()

    def set_deleted_at(self) -> None:
        self.deleted_at = utc_now()


class RecordModel(TimestampedModel):
    __abstract__ = True

    # default=uuid4 generates UUID in Python (available before flush).
    # server_default is a fallback for raw SQL operations (e.g. bulk pg_insert).
    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.id == __value.id

    def __hash__(self) -> int:
        return self.id.int

    def __repr__(self) -> str:
        insp = inspect(self)
        if insp.identity is not None:
            id_value = insp.identity[0]
            return f"{self.__class__.__name__}(id={id_value!r})"
        return f"{self.__class__.__name__}(id=None)"
