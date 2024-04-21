from typing import Optional, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from contacts.orms import ContactORM


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_pwd: Mapped[str] = mapped_column()
    loggedin: Mapped[Optional[bool]] = mapped_column(default=False)
    # refresh_token: Mapped[str] = mapped_column()
    full_name: Mapped[Optional[str]] = mapped_column(default=None,
                                                     unique=True,
                                                     nullable=True)
    contacts: Mapped[Optional[List[ContactORM]]] = relationship()
