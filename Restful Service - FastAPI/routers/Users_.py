from fastapi import APIRouter, status, Depends, Response, HTTPException, Query
from typing import Annotated, Optional, List, Union

from sqlalchemy.orm import Session
from databases import users, get_db
from models import Users
from schemas import Message, GET_Users, POST_Users
from repository.user import users_list, create_users, Hash

router = APIRouter(
    prefix='/users',
    tags = ['users']
)

@router.get('/', status_code=status.HTTP_200_OK, response_model = Union[List[GET_Users], Message])
async def get_users( 
    response: Response, 
    db: Annotated[Session, Depends(get_db)],
    query: str | None = Query(default='db', title='alias for local or db session', max_length=2)
    # id: int | None = Query(default=None, title='retrieve the specific User ID', gt=0) # passing as query parameter to retrieve the individual user_id 
    ) -> list[GET_Users]:
    return users_list(response=response, db=db, query=query)

@router.post('/', status_code=status.HTTP_200_OK)
async def post_users(user: POST_Users, db: Annotated[Session, Depends(get_db)], response: Response):
    return create_users(user=user, db=db, response=response)
"""
{
  "name": "Vinay",
  "email": "vinay@email.com",
  "password": "password",
  "movie_id": 1
}
"""

