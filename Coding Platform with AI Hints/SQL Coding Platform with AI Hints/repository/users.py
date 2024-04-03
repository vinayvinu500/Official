from fastapi import Query, Depends, HTTPException, Response, status
from typing import Annotated

# data
from sqlalchemy.orm import Session
from databases import get_sqlite_db
from models import Users
from schemas import POST_Users, GET_Users
from hashing import Hash


def users_list(response: Response, db: Annotated[Session, Depends(get_sqlite_db)]) -> list[GET_Users]:
    
    if db.query(Users).all() in ([], None):
        # response.status_code = status.HTTP_204_NO_CONTENT
        # return {'message': 'No Users are available in the Database!'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Users are available in the Database!")
    
    users_db = db.query(Users).all()
    return users_db




def create_users(user: POST_Users, db: Annotated[Session, Depends(get_sqlite_db)], response: Response):
    hashing = Hash() # Hashing the pasword!

    if db.query(Users).filter(Users.name.like(f"{user.name.lower()}%")).first() is not None:
        response.status_code = status.HTTP_208_ALREADY_REPORTED
        return {'message': f"User with '{user.name}' is already exist's in the Database!"}

    user_detail = Users(name=user.name.lower(), email=user.email.lower(), passwd=hashing.encrypt(user.password))
    db.add(user_detail)
    db.commit()
    db.refresh(user_detail)

    response.status_code = status.HTTP_201_CREATED
    return {'message': 'User Created: %s' % user_detail}

