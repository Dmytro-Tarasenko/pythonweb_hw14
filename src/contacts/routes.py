from typing import Any

from fastapi import APIRouter, Depends, status
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
    return [ContactResponse.from_orm(_) for _ in db.query(ContactORM).all()]


@router.get("/{contact_id:int}", response_model=ContactResponse)
async def read_id(contact_id: int,
                  db: Session = Depends(get_db)
                  ) -> Any:
    res = db.get(ContactORM, contact_id)
    if res is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=f"Contact with id {contact_id} not found")
    return ContactResponse.from_orm(res)


@router.post("/")
async def create(
        contact: Contact,
        db: Session = Depends(get_db)
) -> ContactResponse:
    pass


@router.put("/{contact_id:int}/{field:str}")
async def add_data(
        contact_id: int,
        field: str,
        db: Session = Depends(get_db)
) -> ContactResponse:
    pass
