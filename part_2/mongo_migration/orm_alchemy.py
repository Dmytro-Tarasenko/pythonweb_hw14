"""SQLAlchemy ORM for the mongo_migration database."""
from os import getenv
from typing import List, Optional

from sqlalchemy import ForeignKey, create_engine, Table, Column
from sqlalchemy.orm import (declarative_base,
                            mapped_column,
                            relationship,
                            Mapped,
                            sessionmaker)

from dotenv import load_dotenv

load_dotenv()

# engine = create_engine('sqlite:///../hw10.sqlite3')
engine = create_engine('postgresql://guest:guest@localhost:5432/hw10')
DBSession = sessionmaker(bind=engine)

Base = declarative_base()


tags_quotes_association = Table(
    "app_quotes_quote_tags",
    Base.metadata,
    Column("quote_id", ForeignKey("app_quotes_quote.id"), primary_key=True),
    Column("tag_id", ForeignKey("app_quotes_tag.id"), primary_key=True)
)

quotes_tag_association = Table(
    "app_quotes_tag_quotes",
    Base.metadata,
    Column("tag_id", ForeignKey("app_quotes_tag.id"), primary_key=True),
    Column("quote_id", ForeignKey("app_quotes_quote.id"), primary_key=True)
)


class TagSQL(Base):
    """SQLAlchemy Tag Model."""
    __tablename__ = "app_quotes_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(unique=True)
    quotes: Mapped[Optional[List["QuoteSQL"]]] = relationship(
        secondary=quotes_tag_association,
        back_populates="tags"
    )


class QuoteSQL(Base):
    """SQLAlchemy Quote Model."""
    __tablename__ = "app_quotes_quote"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("app_quotes_author.id"))
    quote: Mapped[str] = mapped_column(nullable=False)
    author: Mapped["AuthorSQL"] = relationship(
        back_populates="quotes"
    )
    tags: Mapped[Optional[List["TagSQL"]]] = relationship(
        secondary=tags_quotes_association,
        back_populates="quotes"
    )


class AuthorSQL(Base):
    """SQLAlchemy Author Model."""
    __tablename__ = "app_quotes_author"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(nullable=False,
                                        unique=True)
    born_date: Mapped[Optional[str]] = mapped_column()
    born_location: Mapped[Optional[str]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    quotes: Mapped[Optional[List[QuoteSQL]]] = relationship(
        back_populates="author"
    )


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    author1 = AuthorSQL(fullname="John Doe",
                        born_date="2000-01-01",
                        born_location="USA",
                        description="A mysterious")
    author2 = AuthorSQL(fullname="Jane Doe",
                        born_date="2002-02-02",
                        born_location="Canada",
                        description="Cute")
    tag1 = TagSQL(tag="greeting")
    tag2 = TagSQL(tag="world")
    tag3 = TagSQL(tag="hello")

    with DBSession() as session:
        # session.add(author1)
        # session.add(author2)
        # session.add(tag1)
        # session.add(tag3)
        # session.add(tag2)
        # session.commit()
        # author = session.query(AuthorSQL)\
        #     .filter_by(fullname="John Doe").first()
        quote1 = QuoteSQL(author=author1,
                          quote="Hello, World!",
                          tags=[tag1, tag2])
        # author2 = session.query(AuthorSQL)\
        #     .filter_by(fullname="Jane Doe").first()
        quote2 = QuoteSQL(author=author1,
                          quote="4 None Blond!",
                          tags=[tag3, tag2, tag1])
        session.add(quote1)
        session.commit()
        session.add(quote2)
        session.commit()
