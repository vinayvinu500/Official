from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas import POST_Login, POST_Token
from sqlalchemy.orm import Session
from typing import Annotated, List
from databases import get_db
from models import Users
from repository.user import Hash

from datetime import datetime, timedelta
from tokens import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

router = APIRouter(
    tags=['Authentication']
)

hash = Hash()

@router.post('/login', response_model=POST_Token)
async def post_login(db: Annotated[Session, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> POST_Token:

    user_db = db.query(Users).filter(Users.email == form_data.username).first()

    if user_db in ([], None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!", headers={"WWW-Authenticate": "Bearer"})

    
    if not hash.verify(form_data.password, user_db.passwd):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Username or Password!", headers={"WWW-Authenticate": "Bearer"})
    

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_db.email}, 
        expires_delta=access_token_expires
    )
    return POST_Token(access_token=access_token, token_type="bearer")
    