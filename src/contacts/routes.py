import re
from datetime import date, timedelta
from typing import Any, TypeAlias, Literal, List
from pickle import dumps
from json import dumps as jdumps


from fastapi import APIRouter, Depends, status
from sqlalchemy import column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from db import get_db, ContactORM
from contacts.models import Contact, ContactResponse

router = APIRouter(prefix='/contacts',
                   tags=['contacts'])


@router.get("/")
async def read(
        db: Session = Depends(get_db)
) -> list[ContactResponse]:
    """Return all contacts from the database."""
    return [ContactResponse.from_orm(_) for _ in db.query(ContactORM).all()]


@router.get("/{contact_id:int}", response_model=ContactResponse)
async def read_id(contact_id: int,
                  db: Session = Depends(get_db)
                  ) -> Any:
    """Return a contact by id."""
    res = db.get(ContactORM, contact_id)
    if res is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=f"Contact with id {contact_id} not found")
    return ContactResponse.from_orm(res)


@router.post("/", response_model=ContactResponse)
async def create(
        contact: Contact,
        db: Session = Depends(get_db)
) -> Any:
    """Create a new contact."""
    db.add(ContactORM(**contact.model_dump(exclude={'full_name'})))
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if re.search(r"UNIQUE constraint failed", str(e)):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "details": [
                        {"type":
                         "ValueError"},
                        {"msg":
                         "Contact with such fullname or email already exists"}
                    ]})
    except Exception:
        db.rollback()
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={
                                "details": [
                                    {"type": "ValueError"},
                                    {"msg": "Unknown data format"}
                                ]
                            }
                            )
    res = db.query(ContactORM).filter_by(first_name=contact.first_name,
                                         last_name=contact.last_name).first()
    return ContactResponse.from_orm(res)


def get_field_names(model: "BaseModel") -> List[str]:
    """Return a list of field names for the model."""
    fields = list(model.model_fields.keys())
    fields.extend(list(model.model_computed_fields.keys()))
    return fields

ContactFields: TypeAlias = Literal[*get_field_names(Contact)]


@router.get("/find", response_model=List[ContactResponse])
async def find_contact(
        value: str,
        db: Session = Depends(get_db),
        field: ContactFields = "full_name"
) -> Any:
    if field != "full_name":
        if len(value) == 0:
            res = db.query(ContactORM)\
                .filter(column(field).is_(None)).all()
        else:
            search_condition = f"%{value}%"
            print(search_condition)
            res = db.query(ContactORM)\
                .filter(column(field)\
                        .like(search_condition)).all()

        if len(res) == 0:
            return JSONResponse(status_code=404,
                                content={
                                    "details": [
                                        {
                                            "msg": f"There is no result for {field}={value} "
                                        }
                                    ]
                                })
        return [ContactResponse.from_orm(_) for _ in res]
    else:
        try:
            first_name, last_name = value.split(" ", maxsplit=1)
        except:
            first_name = value
            last_name = None
        return JSONResponse(status_code=200,
                            content=f"Fullname search  for {first_name} {last_name}")


@router.get("/bd_mates", response_model=List[ContactResponse])
async def get_birthday_mates_default(
        db: Session = Depends(get_db)
) -> Any:
    """Return contacts with birthday in the next 7 days."""
    return await get_birthday_mates(
        days=7,
        db=db
    )


@router.get("/bd_mates/{days:int}", response_model=List[ContactResponse])
async def get_birthday_mates(
        days: int,
        db: Session = Depends(get_db)
) -> Any:
    """Return contacts with birthday in the next {days} days.
        :param days: int, number of days to search for birthday mates
        :return: list of ContactResponse objects
    """
    res = []
    request_md = []
    for i in range(days):
        month_day = (date.today()+timedelta(days=i)).strftime("%m-%d")
        request_md.append(month_day)
    for md in request_md:
        part = db.query(ContactORM)\
            .filter(ContactORM.birthday.like(f"%{md}")).all()
        res.extend(part)
    if len(res) == 0:
        return JSONResponse(
            status_code=404,
            content={
                "details": [
                    {
                        "msg": f"There is no Birthday mates in {days} day(s)"
                    }
                ]
            }
        )
    return [ContactResponse.from_orm(_) for _ in res]

  
@router.put("/{contact_id:int}/add/{field:str}/{value}",
            response_model=ContactResponse)
async def add_data(
        contact_id: int,
        field: ContactFields,
        value: Any,
        db: Session = Depends(get_db)
) -> Any:
    """Add data to the contact."""
    contact = db.get(ContactORM, contact_id)

    if contact is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "details": [
                    {"type": "ValueError"},
                    {"msg": f"Contact with id {contact_id} not found"}
                ]
            }
        )

    if contact.__dict__.get(field) is not None:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "details": [
                    {"type": "ValueError"},
                    {'msg': (f"Field {field} already set."
                             " Use contacts/:id/edit/:field/:value"
                             " to update it.")}
                ]
            })
    if field == 'extra':
        value = dumps(value)

    db.query(ContactORM).filter_by(id=contact_id).update({field: value})
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
                "details": [
                    {"type": "ValueError"},
                    {'msg': f"Data {value} added successfully to {field}"
                            f" for contact with id {contact_id}"}
                ]
            }
    )


@router.delete('/{contact_id:int}')
async def delete(contact_id: int,
                 db: Session = Depends(get_db)
                 ) -> JSONResponse:
    """Delete a contact by id."""
    contact = db.get(ContactORM, contact_id)
    if contact is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "details": [
                    {"type": "ValueError"},
                    {"msg": f"Contact with id {contact_id} not found"}
                ]
            }
        )
    db.delete(contact)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={})
