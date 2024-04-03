from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# declarative base class    
class Movies(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String,nullable=True)
    released = Column(Boolean, nullable=False)

    user_movies = relationship('Users', back_populates='movies_list')

    def __repr__(self):
        return "<Movies(id='%s', name='%s', description='%s', released='%s')>" %(self.id, self.name, self.description, self.released)
    
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    passwd = Column(String, nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=True)

    movies_list = relationship('Movies', back_populates='user_movies')

    def __repr__(self):
        return "<Users(id='%s', name='%s', email='%s', passwd='%s', movie_id='%s')>" %(self.id, self.name, self.email, self.passwd, self.movie_id)

# Create
# from databases import LocalSession
# record = Movies(id=1, name='Vinay', description='Superhero', released=False)
# LocalSession.add(record)
# LocalSession.add_all([Movies(id=1, name='Vinay', description='Superhero', released=False), Movies(id=1, name='Vijay', description='SuperVillan', released=False)])
# LocalSession.commit()
    
# Data Manipulation
# LocalSession.query(Movies.name, Movies.description) # .all() will return KeyedTuple
# LocalSession.query(Movies).filter_by(name ='Vinay').first() # python class-level 
# LocalSession.query(Movies).filter(record.name.in_(['Vinay', 'Vijay'])).all() # sql construct
# LocalSession.query(Movies).order_by(Movie.id)
    
# Update
# record.name='Nani'
# LocalSession.dirty # <IdentitySet([Movies(id='1', name='Nani', description='Superhero', released='False')])>

# Refresh
# LocalSession.new