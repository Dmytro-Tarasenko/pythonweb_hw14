import re
from typing import Any

from fastapi import APIRouter, Depends, status
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
    db.add(ContactORM(**contact.model_dump(exclude={'full_name'})))
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if re.search(r"UNIQUE constraint failed", str(e)):
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                content="Contact with such fullname or email already exists")
    except Exception:
        db.rollback()
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content="Unknown data format")
    res = db.query(ContactORM).filter_by(first_name=contact.first_name,
                                         last_name=contact.last_name).first()
    return ContactResponse.from_orm(res)


@router.put("/{contact_id:int}/{field:str}")
async def add_data(
        contact_id: int,
        field: str,
        db: Session = Depends(get_db)
) -> ContactResponse:
    pass
