from fastapi import APIRouter, status, Response, Depends, Query
from typing import Annotated, List, Union, Optional

# functions
from repository.movie import movies_list, create_movies, alter_movies, remove_movies

# data
from sqlalchemy.orm import Session
from databases import get_db
from schemas import GET_Movie, Message, POST_Movie, PUT_Movie
from tokens import get_current_user



router = APIRouter(
    prefix='/movies',
    tags=['movies']
)


# dynamic query parameter : ? | &(%26) | + (%20)
"""
> http://localhost:8080/movies
> http://localhost:8080/movies?name=Avengers
> http://localhost:8080/movies?limit=3
> http://localhost:8080/movies?offset=1
> http://localhost:8080/movies?limit=3&offset=1
> http://localhost:8080/movies?published=False
> http://localhost:8080/movies?offset=1&limit=3&published=True
> http://localhost:8080/movies?limit=3&name=Avengers
> http://localhost:8080/movies?limit=3&published=False&offset=1&name=Avengers
"""
@router.get('/', status_code=status.HTTP_200_OK, response_model=Union[List[GET_Movie], Message] | GET_Movie)
async def get_movies(
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    query: str | None = Query(default='db', title='alias for local or db session', max_length=2), # Path(..., title='alias for local or db session', default='db') # https://fastapi.tiangolo.com/es/tutorial/query-params-str-validations/
    offset:Optional[int] | None = None, 
    limit:int | None = None, # = Path(None, description='restricts the response', gt=0), 
    published:bool | None = None, # = Path(None, description='represents the released year'), 
    name:Optional[str] = None,
    current_user: GET_Movie = Depends(get_current_user)
    ) : #  -> list[GET_Movie] | list[dict] | Any
    return movies_list(response=response, db=db, query=query, offset=offset, limit=limit, published=published, name=name)

"""
# movies without dynamic routing should be mentioned before the dynamic parameter in this case {id}
# URI: http://localhost:8080/movies/unpublished
@app.get('/movies/unpublished') 
async def movies_unpublished() -> list[dict]:
    db = [{'name':movie['name'], 'description': movie['description']} for movie in movies if not movie['released']] # unpublished
    if db == []: return "Not Found!"
    return db


# movies without dynamic routing should be mentioned before the dynamic parameter in this case {id}
# URI: http://localhost:8080/movies/published
@app.get('/movies/published') 
async def movies_published() -> list[dict]:
    db = [{'name':movie['name'], 'description': movie['description']} for movie in movies if movie['released']] # published
    if db == []: return "Not Found!"
    return db


# movies with specific id
# URI: http://localhost:8080/movies/2
@app.get('/movies/{id}', response_model=GET_Movie)
async def get_movies(id:int):
    db = {movie['id']: index for index, movie in enumerate(movies)}
    if id in db:
        return movies[db[id]]
    return "Not Found!"


# movies with specific id retrieve only names
# URI: http://localhost:8080/movies/2/name
@app.get('/movies/{id}/name')
async def get_movies_name(id:int):
    # retreive the movies name with specific id
    db = {movie['id']: index for index, movie in enumerate(movies)}
    if id in db:
        return movies[db[id]]['name']
    return "Not Found!"

"""

# add new movies
@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_movies(movie: POST_Movie, db: Annotated[Session, Depends(get_db)], response: Response, current_user: GET_Movie = Depends(get_current_user)):
   return create_movies(movie=movie, db=db, response=response)

"""
{
  "name": "Simpsons",
  "description": "World War 3 (2024)",
  "released": false
}

{
  "name": "Battleship",
  "description": "Art of War",
  "released": true
}

{
  "name": "Avengers",
  "description": "Assemble (2026)",
  "released": false
}
"""

# update the movies with the specific id 
# Errors: 422 Unprocessable Entity while parsing the boolean values of Python(True) and Javascript(true)
@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_movies(id:int, movie:PUT_Movie, response: Response, db: Annotated[Session, Depends(get_db)], current_user: GET_Movie = Depends(get_current_user)):
    return alter_movies(id=id, response=response, db=db)

"""
# Note:  ',' should not be added in the body parameter

id: 12
{
  "name": "Battleship (2014)"
}

id: 13
{
  "name": "Miss Marvels (2024)",
  "description": "payback time!",
  "released": true
}

id: 3
{
    "name": "Captain America (2011)"
}
"""


@router.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_movies(id:int, db: Annotated[Session, Depends(get_db)], response: Response, current_user: GET_Movie = Depends(get_current_user)):
    return remove_movies(id=id, db=db, reponse=response)

