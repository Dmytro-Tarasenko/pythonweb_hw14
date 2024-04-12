from datetime import date
from typing import Optional, Any

from sqlalchemy import create_engine, UniqueConstraint, String, Date, BLOB

from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

engine = create_engine("sqlite:///hw11_api.sqlite")
DBSession = sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine)


class Base(DeclarativeBase):
    pass


class ContactORM(Base):
    __tablename__ = "contacts"

    __table_args__ = (
        UniqueConstraint('first_name', 'last_name',
                         name="full_name_uix"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20))
    last_name:  Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(80),
                                                 unique=True)
    birthday: Mapped[Optional[date]] = mapped_column(Date())
    extra: Mapped[Optional[Any]] = mapped_column(BLOB())


async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print(Base.metadata.tables)
