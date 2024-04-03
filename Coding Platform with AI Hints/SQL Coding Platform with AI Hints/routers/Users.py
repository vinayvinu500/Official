from fastapi import APIRouter, status, Depends, Response, HTTPException, Query
from typing import Annotated, Optional, List, Union

from sqlalchemy.orm import Session
from databases import get_sqlite_db
from schemas import Message, GET_Users, POST_Users
from repository.users import users_list, create_users
from tokens import get_current_user

router = APIRouter(
    prefix='/users',
    tags = ['users']
)

@router.get('/', status_code=status.HTTP_200_OK, response_model = Union[List[GET_Users], Message])
async def get_users( 
    response: Response, 
    db: Annotated[Session, Depends(get_sqlite_db)]
    ) -> list[GET_Users]:
    return users_list(response=response, db=db)

@router.post('/', status_code=status.HTTP_200_OK)
async def post_users(user: POST_Users, db: Annotated[Session, Depends(get_sqlite_db)], response: Response):
    return create_users(user=user, db=db, response=response)
"""
{
  "name": "Vinay",
  "email": "vinay@email.com",
  "password": "password"
}
"""

