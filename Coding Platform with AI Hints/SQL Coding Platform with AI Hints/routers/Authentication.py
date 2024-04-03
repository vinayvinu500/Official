from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas import POST_Login, POST_Token, GET_Users, POST_Users, Message
from sqlalchemy.orm import Session
from typing import Annotated, List, Union
from databases import get_sqlite_db
from models import Users
from hashing import Hash

from datetime import datetime, timedelta
from tokens import ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme, create_access_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

router = APIRouter(
    tags=['Authentication']
)
    
hash = Hash()

@router.post('/login', response_model=POST_Token)
async def post_login(db: Annotated[Session, Depends(get_sqlite_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> POST_Token:

    user_db = db.query(Users).filter(Users.email == form_data.username.lower()).first()

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
    

@router.post("/signup") # response_model=Union[POST_Token, Message]
async def signup(user: POST_Users, db: Session = Depends(get_sqlite_db)):
    # Check if the user already exists
    db_user = db.query(Users).filter(Users.email == user.email.lower()).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and create user
    hashed_password = hash.encrypt(user.password)
    user_detail = Users(name=user.name.lower(), email=user.email.lower(), passwd=hashed_password)
    db.add(user_detail)
    db.commit()
    db.refresh(user_detail)

    # Generate token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_detail.email}, 
        expires_delta=access_token_expires  
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/api/token/validate")
async def validate_token(token: str = Depends(oauth2_scheme)):
    try:
        # Attempt to decode the token. This will automatically validate
        # the token's expiration and signature.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # If decode is successful, the token is valid.
        # There's no need to check for a specific username ('sub' claim) here
        # unless your application logic requires it.
        return {"isValid": True}
    except JWTError as e:
        # If there's an error decoding the token (expired, invalid signature, etc.)
        # we consider the token invalid.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
