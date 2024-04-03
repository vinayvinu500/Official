# Authentication Purposes
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from schemas import GET_Token
from sqlalchemy.orm import Session
from models import Users
from databases import get_sqlite_db


SECRET_KEY="10540f9a6fd2de10f07df7e9ffaa6b50a3b0a815889543623efcfd351201fd08" # openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/") # fetch the token from the login route


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_sqlite_db)) -> GET_Token:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials!", headers={"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
        token_data = GET_Token(username=email)
    except JWTError:
        raise credentials_exception
    
    user_db = db.query(Users).filter(Users.email == token_data.username).first()
    if user_db in ([], None):
        raise credentials_exception
    return user_db
    
    
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


"""
# API Validation: Postman 
Post request: http://localhost:8080/login
    - to validate the login details: Body -> Form -> username (Key-field name) - email(Value) | password(Key-field name) - <password> (value)
    - get jwt token: Response -> access_token
GET request: http://localhost:8080/movies
    - Headers: Authorization(Key) | (Value) bearer <access_token>
"""