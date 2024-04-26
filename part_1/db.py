from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, DeclarativeBase

from settings import settings

# engine = create_engine("sqlite:///hw12_api.sqlite")
engine = create_engine(settings.sqlalchemy_url)
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
