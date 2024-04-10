from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, ValidationError, EmailStr, Field
from enum import Enum

class QuestionSubmission(BaseModel):
    title: str
    description: str
    fileName: str
    difficultLevel: str
    databaseSchema: str
    userQuery: str
    sampleSolution: str

class TestMySQLObjects(BaseModel):
    database_schema: str
    sample_solution: str

class HintsDescription(BaseModel):
    userQuery: str
    embedCode: Optional[int] = None  # Assuming this might still be useful

# Model: POST_Users
class POST_Users(BaseModel):
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True) # FastAPIError(fastapi.exceptions.FastAPIError: No Response object was returned.)

# Model: GET Response_Model
class GET_Users(BaseModel):
    name: str
    email: EmailStr
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

# Model: GET
class Message(BaseModel):
    message: str

# class UserInDB(Users):
#     hashed_password: str

class DifficultyLevel(str, Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

class QuestionGeneration(BaseModel):
    language: str
    num_questions: int
    topic: str = Field('basic topic', min_length=2, max_length=255, strip_whitespace=True)
    difficulty_level: DifficultyLevel
