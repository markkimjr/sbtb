from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from sbtb.core.database.base import TimestampedModel


class User(SQLAlchemyBaseUserTableUUID, TimestampedModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    phone_no: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
