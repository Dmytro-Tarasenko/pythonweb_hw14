import re
from typing import Any, TypeAlias, Literal, List

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


def get_field_names(model: "BaseModel") -> List[str]:
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
