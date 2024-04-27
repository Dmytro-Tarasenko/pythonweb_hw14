"""Migration script from MongoDB to PostgreSQL"""
from typing import Dict

from sqlalchemy.orm import sessionmaker
from orm_alchemy import TagSQL, AuthorSQL, QuoteSQL, Base, engine
from odm_mongo import AuthorMongo, QuoteMongo


# Base.metadata.create_all(engine)
DBSession = sessionmaker(engine)

authors: Dict[str, AuthorSQL] = dict()
tags: Dict[str, TagSQL] = dict()

for quote_mongo in QuoteMongo.objects:

    author_mongo: AuthorMongo = quote_mongo.author

    tags_mongo = quote_mongo.tags

    quote_tags = [tags.setdefault(tag_, TagSQL(tag=tag_))
                  for tag_ in tags_mongo]

    candidate = AuthorSQL(fullname=author_mongo.fullname,
                          born_date=author_mongo.born_date,
                          born_location=author_mongo.born_location,
                          description=author_mongo.description)

    author = authors.setdefault(candidate.fullname, candidate)

    quote = QuoteSQL(quote=quote_mongo.quote,
                     author=author,
                     tags=quote_tags)

    with DBSession() as session:
        session.add(quote)
        session.commit()
        print(f"Quote for {quote.author.fullname} with tags: "
              f"{quote.tags} added.")
