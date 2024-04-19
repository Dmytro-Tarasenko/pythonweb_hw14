from random import randint

import sqlalchemy
from faker import Faker
from db import DBSession

from auth.orms import User
from auth.service import Authentication
from contacts.orms import ContactORM

fake = Faker('uk_UA')

auth = Authentication()

for _ in range(5):
    email = fake.email()
    password = auth.hash_password(plain_password="password")
    user = User(email=email,
                hashed_pwd=password)
    with DBSession() as session:
        session.add(user)
        session.commit()


for _ in range(111):
    first_name = fake.first_name()
    last_name = fake.last_name()
    owner = randint(1, 5)
    if randint(0, 9) > 3:
        email = fake.email()
    else:
        email = None
    if randint(0, 9) >=  2:
        phone = (fake.phone_number()
                 .replace(" ", "")
                 .replace("(", "")
                 .replace(")", "")
                 .replace("+", "")
                 .replace("-", ""))
    else:
        phone = None
    if randint(0, 9) > 3:
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=70)
    else:
        birthday = None
    if randint(0, 9) > 4:
        email = fake.email()
    else:
        email = None
    if randint(0, 9) > 7:
        extra = fake.sentence(nb_words=15)
    else:
        extra = None

    contact = ContactORM(first_name=first_name,
                         last_name=last_name,
                         phone=phone,
                         email=email,
                         birthday=birthday,
                         extra=extra,
                         owner=owner)

    with DBSession() as session:
        try:
            session.add(contact)
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
