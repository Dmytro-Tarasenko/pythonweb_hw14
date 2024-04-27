from django.db.models import (Model,
                              CharField,
                              DateField,
                              TextField,
                              ManyToManyField,
                              ForeignKey,
                              ManyToOneRel,
                              CASCADE)
# Create your models here.


class Tag(Model):
    tag = CharField(max_length=100, unique=True)
    quotes = ManyToManyField('Quote')

    def __str__(self):
        return self.tag


class Quote(Model):
    quote = TextField()
    author = ForeignKey('Author', on_delete=CASCADE)
    tags = ManyToManyField(Tag)

    def __str__(self):
        return f"{self.author}: {self.quote[:50]}"


class Author(Model):
    fullname = CharField(max_length=100)
    born_date = CharField(max_length=100)
    born_location = CharField(max_length=100)
    description = TextField()
    # quotes = ManyToOneRel(to=Quote, field='author')

    def __str__(self):
        return f"{self.fullname} {self.born_date}"
