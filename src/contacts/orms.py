from datetime import date
from typing import Optional

from sqlalchemy import String, Date, Any
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class ContactORM(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20))
    last_name:  Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(80))
    birthday: Mapped[Optional[date]] = mapped_column(Date())
    extra: Mapped[Optional[Any]] = mapped_column(Any())
