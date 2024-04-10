from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field, PastDate, computed_field


class Contact(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(min_length=6,
                                 default=None,
                                 pettern=r"(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5} ?-?[0-9]{4}( ?-?[0-9]{3})")
    birthday: Optional[PastDate] = None
    extra: Optional[Any] = None

    @computed_field
    @property
    def full_name(self) -> str:
        lname = ' ' + self.last_name if self.last_name else ''
        return self.first_name + lname
