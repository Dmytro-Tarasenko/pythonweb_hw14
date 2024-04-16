from datetime import date
from typing import Optional, Any

from sqlalchemy import create_engine, String, Date, Text

from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

# engine = create_engine("sqlite:///hw11_api.sqlite")
engine = create_engine('postgresql://guest:guest@localhost:5432/hw11_api')
DBSession = sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine)


class Base(DeclarativeBase):
    pass


def full_name_calculated_default(context) -> str:
    first = context.get_current_parameters().get('first_name')
    last = context.get_current_parameters().get('last_name')
    last = f" {last}" if last is not None else ""
    return f"{first}{last}"


def full_name_calculated_update(context) -> Any:
    first = context.get_current_parameters().get('first_name')
    last = context.get_current_parameters().get('last_name')
    id_ = context.get_current_parameters().get('id_1')
    if id_ is None:
        return
    with DBSession() as session:
        current = session.get(ContactORM, id_)
        first = first if first is not None else current.first_name
        last = last if last is not None else current.last_name
    last = f" {last}" if last is not None else ""
    return f"{first}{last}"


class ContactORM(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20))
    last_name:  Mapped[Optional[str]] = mapped_column(String(20))
    full_name: Mapped[str] = mapped_column(String(),
                                           unique=True,
                                           default=full_name_calculated_default,
                                           onupdate=full_name_calculated_update)
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    email: Mapped[Optional[str]] = mapped_column(String(80),
                                                 unique=True)
    birthday: Mapped[Optional[date]] = mapped_column(Date())
    extra: Mapped[Optional[Any]] = mapped_column(Text())


async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print(Base.metadata.tables)
