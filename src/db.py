from datetime import date
from typing import Optional, Any

from sqlalchemy import create_engine, String, Date, Text

from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

engine = create_engine("sqlite:///hw12_api.sqlite")
# engine = create_engine('postgresql://guest:guest@localhost:5432/hw12_api')
DBSession = sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine)


class Base(DeclarativeBase):
    pass


async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print(Base.metadata.tables)
