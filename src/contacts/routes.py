from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db, ContactORM
from contacts.models import Contact, ContactResponse

router = APIRouter(prefix='/contacts',
                   tags=['contacts'])


@router.get("/")
async def read(
        db: Session = Depends(get_db)
) -> list[ContactResponse]:
    return [ContactResponse.from_orm(_) for _ in db.query(ContactORM).all()]


@router.get("/{contact_id:int}")
async def read_id(contact_id: int,
                  db: Session = Depends(get_db)
                  ) -> ContactResponse:
    res = db.get(ContactORM, contact_id)
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
