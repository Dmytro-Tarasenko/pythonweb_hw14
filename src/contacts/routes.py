from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from contacts.models import Contact, ContactResponse

router = APIRouter(prefix='/contacts',
                   tags=['contacts'])


@router.get("/")
async def read(
        db: Session = Depends(get_db)
) -> list[ContactResponse]:
    pass


@router.post("/")
async def create(
        contact: Contact,
        db: Session = Depends(get_db)
) -> ContactResponse:
    pass


@router.put("/{contact_id:int}/{field:str}")
async def add_data(
        contact_id: int,
        field: str
) -> ContactResponse:
    pass
