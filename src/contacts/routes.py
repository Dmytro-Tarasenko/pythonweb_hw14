import re
from pickle import dumps
from json import dumps as jdumps
from typing import Any, Literal, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from db import get_db, ContactORM
from contacts.models import Contact, ContactResponse

router = APIRouter(prefix='/contacts',
                   tags=['contacts'])
ContactFields: TypeAlias = Literal[*(str(_) for _ in Contact.model_fields)]


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
