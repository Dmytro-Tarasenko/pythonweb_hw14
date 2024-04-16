from typing import Optional, Any

from pydantic import (BaseModel,
                      EmailStr,
                      Field,
                      PastDate,
                      computed_field,
                      ConfigDict)


class Contact(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(min_length=6,
                                 max_length=15,
                                 pattern=r'[0-9]*',
                                 default=None)
    birthday: Optional[PastDate] = None
    extra: Optional[Any] = None

    @computed_field
    @property
    def full_name(self) -> str:
        lname = ' ' + self.last_name if self.last_name else ''
        return self.first_name + lname


class ContactResponse(Contact):
    model_config = ConfigDict(from_attributes=True)

    id: int


if __name__ == "__main__":
    print([_ for _ in Contact.model_fields])
