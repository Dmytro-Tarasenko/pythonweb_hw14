from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///hw11_api.sqlite")
DBSession = sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine)

Base = DeclarativeBase()


async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
