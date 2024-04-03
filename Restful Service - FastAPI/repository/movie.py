from fastapi import Query, Depends, HTTPException, Response, status
from typing import Annotated, List, Union, Optional

# data
from sqlalchemy.orm import Session
import databases, models, schemas


def movies_list(
    response: Response,
    db: Annotated[Session, Depends(databases.get_db)],
    query: str | None = Query(default='db', title='alias for local or db session', max_length=2), # Path(..., title='alias for local or db session', default='db') # https://fastapi.tiangolo.com/es/tutorial/query-params-str-validations/
    offset:Optional[int] | None = None, 
    limit:int | None = None, # = Path(None, description='restricts the response', gt=0), 
    published:bool | None = None, # = Path(None, description='represents the released year'), 
    name:Optional[str] = None
    ) : #  -> list[schemas.GET_Movie] | list[dict] | Any

    if query not in ('db', None):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"Should be included <query=db> as query parameter!"}
    
    if databases.movies == [] or db.query(models.Movies).all() is None:
        # response.status_code = status.HTTP_204_NO_CONTENT
        # return {"message": "No Records are available in the database!"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No Movie Records are available in the database!')


    # Efficient: only invoke to the specific function without manual checks using multiple if-statements
    def get_movies(query=None, name=None, offset=None, limit=None, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).all()
            return movies_db
        return databases.movies

    # name
    def get_name(query, name, offset=None, limit=None, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).filter(models.Movies.name.like(f'{name}%')).all()
            return movies_db
        keyword = name.split()[0] # handle the input request with startswith one word
        movies_db = [movie for movie in databases.movies if keyword.lower() in movie['name'].lower()]
        return movies_db

    # offset
    def get_offset(query, offset, name=None, limit=None, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).all()
            return movies_db[offset-1:]     
        return databases.movies[offset-1:]

    # limit
    def get_limit(query, limit, name=None, offset=None, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).all()
            return movies_db[:limit]
        return databases.movies[:limit]

    # published
    def get_published(query, published, name=None, offset=None, limit=None):
        if query == 'db':
            movies_db = db.query(models.Movies.name, models.Movies.description).filter(models.Movies.released == published).all()
            return movies_db
        movies_db = [{'name':movie['name'], 'description': movie['description']} for movie in databases.movies if movie['released'] == published] # dynamic published
        return movies_db
    
    # name, published
    def get_name_published(query, name, published, offset=None, limit=None):
        if query == 'db':
            movies_db = db.query(models.Movies).filter(models.Movies.name.like(f'{name}%'), models.Movies.released == published).all()
            return {"message": "No Movies Found!"} if len(movies_db) == 0 else movies_db
        keyword = name.split()[0] # handle the input request with startswith one word
        movies_db = [movie for movie in databases.movies if keyword.lower() in movie['name'].lower() and movie['released'] == published]
        return {"message": "No Movies Found!"} if len(movies_db) == 0 else movies_db
    
    def get_name_published_limit(query, name, published, limit, offset=None):
        if query == 'db':
            movies_db = db.query(models.Movies).filter(models.Movies.name.like(f'{name}%'), models.Movies.released == published).all()
            return {"message": "No Movies Found!"} if len(movies_db[:limit]) == 0 else movies_db[:limit]
        keyword = name.split()[0] # handle the input request with startswith one word
        movies_db = [movie for movie in databases.movies if keyword.lower() in movie['name'].lower() and movie['released'] == published]
        return {"message": "No Movies Found!"} if len(movies_db[:limit]) == 0 else movies_db[:limit]

    # name, limit
    def get_name_limit(query, name, limit, offset=None, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).filter(models.Movies.name.like(f'{name}%')).all()
            return {"message": "No Movies Found!"} if len(movies_db[:limit]) == 0 else movies_db[:limit]
        keyword = name.split()[0] # handle the input request with startswith one word
        movies_db = [movie for movie in databases.movies if keyword.lower() in movie['name'].lower()]
        return {"message": "No Movies Found!"} if len(movies_db[:limit]) == 0 else movies_db[:limit]
    
    # name, offset, limit
    def get_name_offset_limit(query, name, limit, offset, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).filter(models.Movies.name.like(f'{name}%')).all()
            return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) == 0 else movies_db[offset-1:offset+limit-1]
        keyword = name.split()[0] # handle the input request with startswith one word
        movies_db = [movie for movie in databases.movies if keyword.lower() in movie['name'].lower()]
        return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) == 0 else movies_db[offset-1:offset+limit-1]

    # offset, limit 
    def get_offset_limit(query, offset, limit, name=None, published=None):
        if query == 'db':
            movies_db = db.query(models.Movies).all()
            return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) == 0 else movies_db[offset-1:offset+limit-1]
        return {"message": "No Movies Found!"} if len(databases.movies[offset-1:offset+limit-1]) == 0 else databases.movies[offset-1:offset+limit-1]

    # limit, published
    def get_published_limit(query, published, limit, name=None, offset=None):
        if query == 'db':
            movies_db = db.query(models.Movies.name, models.Movies.description).filter(models.Movies.released == published).all()
            return {"message": "No Movies Found!"} if len(movies_db[:limit]) == 0 else movies_db[:limit]
        movies_db = [{'name':movie['name'], 'description': movie['description']} for movie in databases.movies if movie['released'] == published] # dynamic published
        return {"message": "No Movies Found!"} if len(movies_db[:limit]) == 0 else movies_db[:limit]
    
    # offset, limit, published
    def get_offset_limit_published(query, offset, limit, published, name=None):
        if query == 'db':   
            movies_db = db.query(models.Movies.name, models.Movies.description).filter(models.Movies.released == published).all()
            return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) == 0 else movies_db[offset-1:offset+limit-1]        
        movies_db = [{'name':movie['name'], 'description': movie['description']} for movie in databases.movies if movie['released'] == published] # dynamic published
        return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) == 0 else movies_db[offset-1:offset+limit-1]
    
    # name, offset, limit, published
    def get_name_offset_limit_published(query, name, offset, limit, published):
        if query == 'db':
            movies_db = db.query(models.Movies).filter(models.Movies.name.like(f'{name}%'), models.Movies.released == published).all()
            return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) < 1 else movies_db[offset-1:offset+limit-1]
        keyword = name.split()[0] # handle the input request with startswith one word
        movies_db = [movie for movie in databases.movies if keyword.lower() in movie['name'].lower() and movie['released'] == published]
        return {"message": "No Movies Found!"} if len(movies_db[offset-1:offset+limit-1]) < 1 else movies_db[offset-1:offset+limit-1]
    
    # (name, offset, limit, published) # query, 
    comb = {
        (False, False, False, None): get_movies, 
        (True, False, False, None): get_name, 
        (False, True, False, None): get_offset, 
        (False, False, True, None): get_limit, 
        (False, False, False, True): get_published, 
        (False, False, False, False): get_published, 
        (True, False, True, None): get_name_limit, 
        (True, False, False, True): get_name_published,
        (True, False, False, False): get_name_published,
        (True, False, True, False): get_name_published_limit,
        (True, False, True, True): get_name_published_limit,
        (True, True, True, None): get_name_offset_limit, 
        (False, True, True, None): get_offset_limit, 
        (False, False, True, True): get_published_limit, 
        (False, False, True, False): get_published_limit, 
        (False, True, True, True): get_offset_limit_published, 
        (False, True, True, False): get_offset_limit_published, 
        (True, True, True, True): get_name_offset_limit_published,
        (True, True, True, False): get_name_offset_limit_published,
        (None, None, None, None, None): get_movies
    }

    params = (query, name, offset, limit, published)
    print("Read Request: <READ(query='%s', name='%s', offset='%s', limit='%s', published='%s')>" % params)
    print("Query Params Request: <Params(query='%s', name='%s', offset='%s', limit='%s', published='%s')>" % params)

    params = (bool(name), bool(offset), bool(limit), published) # bool(query), 
    func = comb.get(params, None)
    return {"message": "Not Found!"} if func is None else func(query=query, name=name, offset=offset, limit=limit, published=published)

    # Inefficient
    """
    # no query parameters involved
    if name is None and limit is None and published is None and offset is None:
        return databases.movies
    
    # name with specific keyword in databases.movies['name']
    if name is not None and limit is None and published is None and offset is None:
        keyword = name.split()[0] # handle the input request with startswith one word
        db = [movie for movie in databases.movies if keyword in movie['name']]
        return db
    
    # name with specific keyword in databases.movies['name']
    if name is not None and limit is None and published is None and offset is None:
        keyword = name.split()[0] # handle the input request with startswith one word
        db = [movie for movie in databases.movies if keyword in movie['name']]
        return db
    
    # limit the response 
    if name is None and limit is not None and published is None:
        return databases.movies[:limit]
    
    # offset from the request
    if name is None and limit is None and published is None and offset is not None:
        return databases.movies[offset-1:]
    
    # limit, offset from the request
    if name is None and limit is not None and published is None and offset is not None:
        return databases.movies[offset-1:limit]
    
    # published response
    if name is None and limit is None and published is not None:
        db = [{'name':movie['name'], 'description': movie['description']} for movie in databases.movies if movie['released'] == published] # dynamic published
        return db
    
    # limit, published, offset from the request
    if name is None and limit is not None and published is not None and offset is not None:
        db = [{'name':movie['name'], 'description': movie['description']} for movie in databases.movies if movie['released'] == published] # dynamic published
        return db[offset-1:limit]

    # name, limit from the request
    if name is not None and limit is not None and published is None and offset is None:
        keyword = name.split()[0] # handle the input request with startswith one word
        db = [movie for movie in databases.movies if keyword in movie['name'] and movie['released'] == published]
        return db[:limit]
    
    # name, limit, published, offset from the request
    if name is not None and limit is not None and published is not None and offset is not None:
        keyword = name.split()[0] # handle the input request with startswith one word
        db = [movie for movie in databases.movies if keyword in movie['name'] and movie['released'] == published]
        return db[offset-1:limit]

    """

def create_movies(movie: schemas.POST_Movie, db: Annotated[Session, Depends(databases.get_db)], response: Response):
    if movie.name.split()[0] in [mov['name'].split()[0] for mov in databases.movies] or db.query(models.Movies).filter(models.Movies.name.like(f'{movie.name.split()[0]}%')).first() is not None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Can't Add movie '{movie.name}' which exist's!"}
    
    # Local
    _id = max(databases.movies, key=lambda x: x['id'])['id'] + 1
    databases.movies.append({'id':_id, 'name':movie.name, 'description':movie.description, 'released':movie.released})

    # DB
    new_movie = models.Movies(name=movie.name, description=movie.description, released=movie.released)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    return {'message': f"Successfully Added the Movie list at Local: {len(databases.movies)-1} with {databases.movies[-1]} | Database: {db.query(models.Movies.id).count()} with {db.query(models.Movies).order_by(models.Movies.id.desc()).first()}"}

def alter_movies(id:int, movie:schemas.PUT_Movie, response: Response, db: Annotated[Session, Depends(databases.get_db)]):
    # id exists or not
    if id not in [mov['id'] for mov in databases.movies] or db.query(models.Movies).filter(models.Movies.id == id).first() is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': f"Can't locate the ID: {id} in the database!"}
    ind = [ind for ind, mov in enumerate(databases.movies) if mov['id'] == id][0]
    # databases.movies[ind].update(movie) # instance of movie: Movie (pydantic) can't be updated like in case of dict

    # name exists or not
    if movie.name.split()[0] in [mov['name'].split()[0] for mov in databases.movies] or db.query(models.Movies).filter(models.Movies.name.like(f'{movie.name.split()[0]}%')) is None:
        response.status_code = status.HTTP_302_FOUND
        return {"message": f"Record already Exist's with name: '{movie.name.split()[0]}' in the database!"}
    
    def update_name(name, description = None, released=None):
        prev_name = databases.movies[ind]['name']
        if prev_name != movie.name:
            databases.movies[ind]['name'] = movie.name
            db.query(models.Movies).filter(models.Movies.id == id).update({"name": movie.name}, synchronize_session='fetch')
            db.commit()
            return {'message': f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}"'}
        return {'message': f"Can't Update the name, since there is no change in previous value: '{prev_name}' | latest value: '{movie.name}'"}

    def update_description(description, name = None, released = None):
        prev_description = databases.movies[ind]['description']
        if prev_description != movie.description:
            databases.movies[ind]['description'] = movie.description
            db.query(models.Movies).filter(models.Movies.id == id).update({"description": movie.description}, synchronize_session='fetch')
            db.commit()
            return {'message': f'Successfully Updated the description with previous value: "{prev_description}" | latest value: "{movie.description}"'}
        return {'message': f"Can't Update the description, since there is no change in previous value: '{prev_description}' | latest value: '{movie.description}'"}


    def update_released(released, name=None, description=None):
        prev_released = databases.movies[ind]['released']
        if prev_released != movie.released:
            databases.movies[ind]['released'] = movie.released
            db.query(models.Movies).filter(models.Movies.id == id).update({"released": movie.released}, synchronize_session='fetch')
            db.commit()
            return {'message': f'Successfully Updated the released with previous value: "{prev_released}" | latest value: "{movie.released}"'}
        return {'message': f"Can't Update the released, since there is no change in previous value: '{prev_released}' | latest value: '{movie.released}'"}

    def update_name_description(name, description, released=None):
        prev_name = databases.movies[ind]['name']
        prev_description = databases.movies[ind]['description']
        if prev_name != movie.name and prev_description != movie.description:
            databases.movies[ind]['name'] = movie.name
            databases.movies[ind]['description'] = movie.description
            db.query(models.Movies).filter(models.Movies.id == id).update({"name": movie.name, "description": movie.description}, synchronize_session='fetch')
            db.commit()
            return {"message": f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}" and description with previous value: "{prev_description}" | latest value: {movie.description}'}
        elif prev_name == movie.name:
           return {'message': f"Can't Update the name, since there is no change in previous value: '{prev_name}' | latest value: '{movie.name}'"}
        elif prev_description == movie.description:
            return {'message': f"Can't Update the description, since there is no change in previous value: '{prev_description}' | latest value: '{movie.description}'"}
        else:
            return {'message': f"Can't Update the name, since there is no change in previous value: '{prev_name}' | latest value: '{movie.name}' and the description is of no change with previous value: '{prev_description}' | latest value: '{movie.description}'"}
            

    def update_name_released(name, released, description = None):
        prev_name = databases.movies[ind]['name']
        prev_released = databases.movies[ind]['released']
        if prev_name != movie.name and prev_released != movie.released:
            databases.movies[ind]['name'] = movie.name
            databases.movies[ind]['released'] = movie.released

            db.query(models.Movies).filter(models.Movies.id == id).update({"name": movie.name, "released": movie.released}, synchronize_session='fetch')
            db.commit()
            return {"message": f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}" and released with previous value: "{prev_released}" | latest value: "{movie.released}"'}
        elif prev_name == movie.name:
           return {'message': f"Can't Update the name, since there is no change in previous value: '{prev_name}' | latest value: '{movie.name}'"}
        elif prev_released == movie.released:
            return {'message': f"Can't Update the released, since there is no change in previous value: '{prev_released}' | latest value: '{movie.released}'"}
        else:
            return {'message': f"Can't Update the name, since there is no change in previous value: '{prev_name}' | latest value: '{movie.name}' and the released is of no change with previous value: '{prev_released}' | latest value: '{movie.released}'"}


    def update_description_released(description, released, name=None):
        prev_description = databases.movies[ind]['description']
        prev_released = databases.movies[ind]['released']
        if prev_description != movie.description and prev_released != movie.released:
            databases.movies[ind]['description'] = movie.description
            databases.movies[ind]['released'] = movie.released

            db.query(models.Movies).filter(models.Movies.id == id).update({"description": movie.description, "released": movie.released}, synchronize_session='fetch')
            db.commit()
            return {"message": f'Successfully Updated the description with previous value: "{prev_description}" | latest value: "{movie.description}" and released with previous value: "{prev_released}" | latest value: "{movie.released}"'}
        elif prev_description == movie.description:
           return {'message': f"Can't Update the description, since there is no change in previous value: '{prev_description}' | latest value: '{movie.description}'"}
        elif prev_released == movie.released:
            return {'message': f"Can't Update the released, since there is no change in previous value: '{prev_released}' | latest value: '{movie.released}'"}
        else:
            return {'message': f"Can't Update the description, since there is no change in previous value: '{prev_description}' | latest value: '{movie.description}' and the released is of no change with previous value: '{prev_released}' | latest value: '{movie.released}'"}

    def update_name_description_released(name, description, released):
        prev_name = databases.movies[ind]['name']
        prev_description = databases.movies[ind]['description']
        prev_released = databases.movies[ind]['released']
        databases.movies[ind]['name'] = movie.name
        databases.movies[ind]['description'] = movie.description
        databases.movies[ind]['released'] = movie.released

        db.query(models.Movies).filter(models.Movies.id == id).update({"name": movie.name, "description": movie.description, "released": movie.released}, synchronize_session='fetch')
        db.commit()

        params = (prev_name != movie.name, prev_description != movie.description, prev_released != movie.released)

        # track_changes: (name, description, released)
        track_changes = {
            (True, True, True): {"message": f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}", description with previous value: "{prev_description}" | latest value: "{movie.description}" and released with previous value: "{prev_released}" | latest value: "{movie.released}"'},
            (True, False, False): {"message": f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}"'},
            (False, True, False): {"message": f'Successfully Updated the description with previous value: "{prev_description}" | latest value: "{movie.description}"'},
            (False, False, True): {"message": f'Successfully Updated the released with previous value: "{prev_released}" | latest value: "{movie.released}"'},
            (True, True, False): {"message": f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}" and description with previous value: "{prev_description}" | latest value: "{movie.description}"'},
            (True, False, True): {"message": f'Successfully Updated the name with previous value: "{prev_name}" | latest value: "{movie.name}" and released with previous value: "{prev_released}" | latest value: "{movie.released}"'},
            (False, True, True): {"message": f'Successfully Updated the name with previous value: "{prev_description}" | latest value: "{movie.description}" and released with previous value: "{prev_released}" | latest value: "{movie.released}"'},
            (False, False, False): {'message': 'There were no Changes done!'},
        }
        
        print("Change Request: <PUT(name='%s', description='%s', released='%s')>" % (movie.name, movie.description, movie.released))
        msg = track_changes.get(params, None) 
        return "Not found!" if msg is None else msg
       
    def no_update(name=None, description=None, released=None):
        return {"message": "No updates are done!"}
 
    # (name, description, released)
    comb = {
        (False, False, None): no_update,
        (True, True, True): update_name_description_released,
        (True, True, False): update_name_description_released,
        (True, False, None): update_name,
        (False, True, None): update_description,
        (False, False, True): update_released,
        (False, False, False): update_released,
        (True, True, None): update_name_description,
        (True, False, True): update_name_released,
        (False, True, True): update_description_released
    }
    params = (bool(movie.name), bool(movie.description), movie.released)
    print("Edit Request: <PUT(name='%s', description='%s', released='%s')>" % params)

    func = comb.get(params, None)

    return {"message": "Not Found!"} if func is None else func(name=movie.name, description=movie.description, released=movie.released)

def remove_movies(id:int, db: Annotated[Session, Depends(databases.get_db)], response: Response):
    if id not in [mov['id'] for mov in databases.movies] or db.query(models.Movies).filter(models.Movies.id == id).first() is None:
        # raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"Can't locate the ID: {id} in the database!")
        response.status_code = status.HTTP_204_NO_CONTENT
        return {"message": f"Can't locate the ID: {id} in the database!"}

    # Local
    ind = [ind for ind, mov in enumerate(databases.movies) if mov['id'] == id][0]
    prev_movie = databases.movies[ind]
    del databases.movies[ind]

    # DB
    record = db.query(models.Movies).filter(models.Movies.id == id).delete(synchronize_session=False)
    db.commit()
    print(f"Database Instance: Deleted one record - {record}")
    return {'message': f'Sucessfully Deleted the records (Local | DB): {prev_movie}'}

