from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime, Enum, String
from datetime import datetime, timezone
import enum

class DifficultyLevel(enum.Enum):
    Easy = 1
    Medium = 2
    Hard = 3


Base = declarative_base()

class CodingQuestions(Base):
    """Monitor and Track of the questions were created and store through sqlite database"""
    __tablename__ = "codingquestionsrepository"

    ID = Column(Integer, primary_key=True, autoincrement=True, index=True)
    Title = Column(Text, unique=True, nullable=False, index=True)
    Description = Column(Text, nullable=False)
    DatabaseSchema = Column(Text, nullable=False, unique=True)
    UserQuery = Column(Text, nullable=True)
    SampleSolution = Column(Text, nullable=False)
    Difficulty = Column(Enum(DifficultyLevel), nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    def __repr__(self):
        return "<CodingQuestions(ID=%s, Title=%s, Description=%s, DatabaseSchema=%s, UserQuery=%s, SampleSolution=%s, Difficulty=%s, CreatedAt=%s, UpdatedAt=%s)>" %(self.ID, self.Title, self.Description, self.DatabaseSchema, self.UserQuery, self.SampleSolution, self.Difficulty, self.CreatedAt, self.UpdatedAt)
    

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    passwd = Column(String, nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))


    def __repr__(self):
        return "<Users(id='%s', name='%s', email='%s', passwd='%s')>" %(self.id, self.name, self.email, self.passwd)