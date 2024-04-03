from fastapi import Query, Depends, HTTPException, Response, status
from typing import Annotated, List, Union, Optional
from passlib.context import CryptContext 

# data
from sqlalchemy.orm import Session
from databases import users, get_db
from models import Users
from schemas import POST_Users, GET_Users


# Encryption
class Hash:
    pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def encrypt(self, paswd: str):
        return self.pwd.hash(paswd)
    
    def verify(self, plain_password, hashed_password):
        return self.pwd.verify(plain_password, hashed_password)


def users_list( 
    response: Response, 
    db: Annotated[Session, Depends(get_db)],
    query: str | None = Query(default='db', title='alias for local or db session', max_length=2)
    ) -> list[GET_Users]:
    
    if query.lower() not in ('db', None):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"Should be included <query=db> as query parameter!"}
    
    if users == [] or db.query(Users).all() in ([], None):
        # response.status_code = status.HTTP_204_NO_CONTENT
        # return {'message': 'No Users are available in the Database!'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Users are available in the Database!")

    
    if query.lower() == 'db':
        users_db = db.query(Users).all()
        return users_db

    return users


def create_users(user: POST_Users, db: Annotated[Session, Depends(get_db)], response: Response):
    hashing = Hash() # Hashing the pasword!

    if user.name.split()[0] in [u['name'].split()[0] for u in users] or db.query(Users).filter(Users.name.like(f"{user.name}%")).first() is not None:
        response.status_code = status.HTTP_208_ALREADY_REPORTED
        return {'message': f"User with '{user.name.title()}' is already exist's in the Database!"}

    # db
    user_detail = Users(name=user.name, email=user.email, passwd=hashing.encrypt(user.password), movie_id=user.movie_id)
    db.add(user_detail)
    db.commit()
    db.refresh(user_detail)

    # local
    users.append({'id':user_detail.id, 'name':user.name, 'email':user.email, 'passwd':hashing.encrypt(user.password), 'movie_id':user.movie_id})

    response.status_code = status.HTTP_201_CREATED
    return {'message': 'User Created: %s' % user_detail}

