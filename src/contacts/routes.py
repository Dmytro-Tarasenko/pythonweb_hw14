import re
from datetime import date, timedelta
from typing import Any, TypeAlias, Literal, List, Annotated

from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from starlette.responses import Response

import db
from contacts.orms import ContactORM
from contacts.models import Contact, ContactResponse
from users.orms import User
from auth.service import Authentication

router = APIRouter(prefix='/contacts',
                   tags=['contacts'])

auth_service = Authentication()


def get_field_names(model: "BaseModel") -> List[str]:
    """Return a list of field names for the model."""
    fields = list(model.model_fields.keys())
    fields.extend(list(model.model_computed_fields.keys()))
    return fields


ContactFields: TypeAlias = Literal[*get_field_names(Contact)]


@router.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def read(
        user: Annotated[User, Depends(auth_service.get_access_user)],
        db: Session = Depends(db.get_db)
) -> list[ContactResponse]:
    """
    Return all contacts from the database.
    Args:
        user (User): user retrieved from 'users' with valid credentials
        db (Session): session object used for database operations

    Returns:
        list of contacts (ContactResponse) or empty list
    """
    return [ContactResponse.from_orm(_) for _ in db.query(ContactORM)\
            .filter(ContactORM.owner == user.id).all()]


@router.get("/{contact_id:int}",
            response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def read_id(contact_id: int,
                  user: Annotated[User, Depends(auth_service.get_access_user)],
                  db: Session = Depends(db.get_db)
                  ) -> Any:
    """
    Retrieves a contact by id.
    Args:
        contact_id (int): identifier of contact in database
        user (User): user retrieved from 'users' with valid credentials,
            also serves as an access filter to user-owned contacts only
        db (Session): session object used for database operations

    Returns:
        ContactResponse model or JSONResponse with status 404 if contact with
        specified id not found in user-owned contacts
    """
    res = db.query(ContactORM.id == contact_id,
                   ContactORM.owner == user.id).first()

    if res is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=f"Contact with id {contact_id} not found")
    return ContactResponse.from_orm(res)


@router.post("/",
             response_model=ContactResponse,
             dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def create(
        contact: Contact,
        user: Annotated[User, Depends(auth_service.get_access_user)],
        db: Session = Depends(db.get_db)
) -> Any:
    """
    Create a new contact.
    Args:
        contact (Contact): model with new contact information
        user (User): user retrieved from 'users' with valid credentials,
            also serves as an access filter to user-owned contacts only
        db (Session): session object used for database operations

    Returns:
        ContactResponse model or JSONResponse with statuses 409 (for contact with
        duplicate unique fields) or 422 (for unprocessable data)
    """
    print(db)
    db.add(ContactORM(**contact.model_dump(exclude={'full_name'}), owner=user.id))
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
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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


@router.get("/find",
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def find_contact(
        value: str,
        db: Annotated[Session, Depends(db.get_db)],
        user: Annotated[User, Depends(auth_service.get_access_user)],
        field: ContactFields = "full_name"
) -> Any:
    """
       Create a new contact.
       Args:
           field (ContactFields): field to search in contacts
           value (str): value to search in field
           user (User): user retrieved from 'users' with valid credentials,
               also serves as an access filter to user-owned contacts only
           db (Session): session object used for database operations

       Returns:
           list of contacts (ContactResponse) or JSONResponse with status code 404
           if there are no result for specified search condictions
    """
    if field != "full_name":
        if len(value) == 0:
            res = db.query(ContactORM)\
                .filter(column(field).is_(None),
                        ContactORM.owner == user.id).all()
        else:
            search_condition = f"%{value}%"
            res = db.query(ContactORM)\
                .filter(column(field).like(search_condition),
                        ContactORM.owner == user.id).all()

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

    res = db.query(ContactORM)\
            .filter(ContactORM.full_name == value)
    if len(res) == 0:
        return JSONResponse(status_code=404,
                            content={
                                "details": [
                                    {
                                        "msg": f"There is no result for {field}={value}"
                                    }
                                ]
                            })
    return [ContactResponse.from_orm(_) for _ in res]


@router.get("/bd_mates",
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def get_birthday_mates_default(
        db: Session = Depends(db.get_db)
) -> Any:
    """
    Return contacts with birthday in the next 7 days.
    Args:
        db (Session): session object used for database operations

   Returns:
       list of contacts (ContactResponse) or JSONResponse with 404 status code
        if there are no birthday mates in a week
    """
    return await get_birthday_mates(
        days=7,
        db=db
    )


@router.get("/bd_mates/{days:int}",
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def get_birthday_mates(
        days: int,
        db: Annotated[Session, Depends(db.get_db)],
        user: Annotated[User, Depends(auth_service.get_access_user)]
) -> Any:
    """
    Return contacts with birthday in the next {days} days.

    Args:
        days (int): number of days to search for birthday mates
        db (Session): session object used for database operations
        user (User): user retrieved from 'users' with valid credentials,
               also serves as an access filter to user-owned contacts only

    Returns:
        list of ContactResponse objects or JSONResponse with 404 status code
        if there are no birthday mates in specified number of days
    """
    res = []
    request_md = []
    for i in range(days):
        month_day = (date.today()+timedelta(days=i)).strftime("%m-%d")
        request_md.append(month_day)
    for md in request_md:
        part = db.query(ContactORM)\
            .filter(ContactORM.birthday.like(f"%{md}"),
                    ContactORM.owner == user.id).all()
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
            response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def add_data(
        contact_id: int,
        field: ContactFields,
        value: str,
        db: Annotated[Session, Depends(db.get_db)],
        user: Annotated[User, Depends(auth_service.get_access_user)]
) -> Any:
    """
    Add data to the contact.

    Args:
        contact_id (int): identifier of contact in database
       field (ContactFields): field to search in contacts
       value (str): value to search in field
       user (User): user retrieved from 'users' with valid credentials,
           also serves as an access filter to user-owned contacts only
       db (Session): session object used for database operations

   Returns:
       JSONResponse`s with status codes:
       201 - on success
       404 - if user-owned contact with specified id is not found
       422 - for unprocessable data
    """
    contact = db.query(ContactORM.id == contact_id,
                       ContactORM.owner == user.id).first()

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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "details": [
                    {"type": "ValueError"},
                    {'msg': (f"Field {field} already set."
                             " Use contacts/:id/edit/:field/:value"
                             " to update it.")}
                ]
            })
    db.query(ContactORM).filter_by(id=contact_id).update({field: value})
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
                "details": [
                    {'msg': f"Data {value} added successfully to {field}"
                            f" for contact with id {contact_id}"}
                ]
            }
    )


@router.patch("/{contact_id:int}/edit/{field:str}/{value:str}",
              response_model=ContactResponse,
              dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def edit_data(
        contact_id: int,
        field: ContactFields,
        value: str,
        db: Annotated[Session, Depends(db.get_db)],
        user: Annotated[User, Depends(auth_service.get_access_user)]
) -> Any:
    """
    Edit data of the contact.

    Args:
        contact_id (int): identifier of contact in database
        field (ContactFields): field to search in contacts
        value (str): value to search in field
        user (User): user retrieved from 'users' with valid credentials,
           also serves as an access filter to user-owned contacts only
        db (Session): session object used for database operations

   Returns:
       JSONResponse`s with status codes:
       201 - on success
       404 - if user-owned contact with specified id is not found
       422 - for unprocessable data
    """
    contact = db.query(ContactORM.id == contact_id,
                       ContactORM.owner == user.id).first()

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

    if contact.__dict__.get(field) is None:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "details": [
                    {"type": "ValueError"},
                    {'msg': (f"Field {field} is not set."
                             " Use contacts/:id/add/:field/:value"
                             " to add it.")}
                ]
            })
    if field == ("full_name"):
        try:
            first, last = value.split(" ", maxsplit=1)
        except:
            first = value
            last = None
        db.query(ContactORM).filter_by(id=contact_id).update({"first_name": first,
                                                              "last_name": last})
        db.commit()
    else:
        db.query(ContactORM).filter_by(id=contact_id).update({field: value})
        db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
                "details": [
                    {'msg': f"{field} changed successfully with data {value}"
                            f" for contact with id {contact_id}"}
                ]
            }
    )


@router.delete('/delete/{contact_id:int}',
               responses={204: {"model": None}},
               dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def delete(
        contact_id: int,
        db: Annotated[Session, Depends(db.get_db)],
        user: Annotated[User, Depends(auth_service.get_access_user)]
) -> Any:
    """
    Delete a contact by id.

    Args:
        contact_id (int): identifier of contact in database
        user (User): user retrieved from 'users' with valid credentials,
           also serves as an access filter to user-owned contacts only
        db (Session): session object used for database operations

   Returns:
       JSONResponse`s with status codes:
       204 - on success
       404 - if user-owned contact with specified id is not found
    """
    contact = db.query(ContactORM.id == contact_id,
                       ContactORM.owner == user.id).first()
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/{contact_id:int}/delete/{field:str}',
               responses={204: {"model": None}},
               dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def delete_data(
        contact_id: int,
        field: ContactFields,
        db: Annotated[Session, Depends(db.get_db)],
        user: Annotated[User, Depends(auth_service.get_access_user)]
) -> Any:
    """
    Delete field for contact with id.

    Args:
        contact_id (int): identifier of contact in database
        field (ContactFields): field to search in contacts
        user (User): user retrieved from 'users' with valid credentials,
           also serves as an access filter to user-owned contacts only
        db (Session): session object used for database operations

   Returns:
       JSONResponse`s with status codes:
       204 - on success
       404 - if user-owned contact with specified id is not found
       422 - for unprocessable data
    """
    contact = db.query(ContactORM.id == contact_id,
                       ContactORM.owner == user.id).first()
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
    if field == "full_name" or field == "first_name":
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "details": [
                    {"type": "ValueError"},
                    {"msg": "Unable to delete required field (first_name or last_name)."
                     "Use /contacts/delete/:id instead."}
                ]
            }
        )
    db.query(ContactORM).filter_by(id=contact_id).update({field: None})
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
