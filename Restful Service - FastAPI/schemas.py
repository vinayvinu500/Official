# Pydantic models
from pydantic import BaseModel, ConfigDict, ValidationError
from typing import List, Optional

# Model: GET
class Message(BaseModel):
    message: str

# Model Relationship: Users -> Movies
class GET_Users_Relationships(BaseModel):
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

# Model: GET Response_Model
class GET_Movie(BaseModel): # extending POST_Movie Model will not be suitable
    name: str
    description: str
    released: bool | None = None 
    user_movies: List[GET_Users_Relationships] | GET_Users_Relationships = []

    model_config = ConfigDict(from_attributes=True)

    # class Config():
    #     from_attributes = True # orm_mode

# Model: POST | PUT
class POST_Movie(BaseModel):
    name: str
    description: str | None = None
    released: bool 

class PUT_Movie(BaseModel):
    name: str | None = None
    description: str | None = None
    released: bool | None = None

# Model: POST_Users
class POST_Users(BaseModel):
    name: str
    email: str
    password: str
    movie_id: int | None = None

    model_config = ConfigDict(from_attributes=True) # FastAPIError(fastapi.exceptions.FastAPIError: No Response object was returned.)


# Model Relationship: Movie -> Users
class GET_Movie_Relationship(BaseModel):
    name: str
    description: str
    released: bool | None = None 
    model_config = ConfigDict(from_attributes=True)

# Model: GET Response_Model
class GET_Users(BaseModel):
    name: str
    email: str
    movie_id: int
    movies_list: List[GET_Movie_Relationship] | GET_Movie_Relationship = []
    model_config = ConfigDict(from_attributes=True)

class POST_Login(BaseModel):
    username: str
    password: str

# Authentication Token
class POST_Token(BaseModel):
    access_token: str
    token_type: str

class GET_Token(BaseModel):
    username: Optional[str] = None