# Import Errors: CircularImport, attempted relative import beyond top-level package

# database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Movies, Users

SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlite.db'
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={'check_same_thread': False})
LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
session = LocalSession()

movies = [
    {'id': 1, 'name': 'IronMan (2008)', 'description': 'Start of Phase I', 'released': True},
    {'id': 2, 'name': 'Avengers (2012)', 'description': 'Avengers Assemble!', 'released': False},
    {'id': 3, 'name': 'Captain America (2010)', 'description': 'Start of Super Serum!', 'released': True},
    {'id': 4, 'name': 'Mermaid (1998)', 'description': 'Start of Super Serum!', 'released': False},
    {'id': 5, 'name': 'Little Angel (1907)', 'description': 'Glimpse of angel from the Darkness', 'released': True},
    {'id': 6, 'name': 'Perfect Blue (1809)', 'description': 'perfect picture of a superstar!', 'released': False},
    {'id': 7, 'name': 'Great Teacher Onizuka (1999)', 'description': 'great teacher qualities!', 'released': False},
    {'id': 8, 'name': 'Avengers: Age of Ultron (2014)', 'description': 'loss of great sheild Iron Robots of web', 'released': True},
    {'id': 9, 'name': 'Avengers: Infinity War (2018)', 'description': 'Starting of great loss', 'released': True},
    {'id': 10, 'name': 'Avengers: Endgame(2019)', 'description': 'New Chapter of next phase - 4', 'released': True},
]

users = [
    {'id': 1, "name":"Vinay", "email":"Vinay@email.com", "passwd": "$2b$12$Rbg9TDAwhfCJNEhbXP2DJOjQZh/yiHybbUrDjT4POTzlA7lWQWS1y", "movie_id": 1}, # Vinay
    {'id': 2, "name":"Vijay", "email":"Vijay@email.com", "passwd": "$2b$12$jNelBSnf9S.95UMSrRRs8uj7qvM0BHGMuGvUMJVeIrJOkNeXVn/z.", "movie_id": 2}, # Vijay
    {'id': 3, "name":"Nani", "email":"Nani@email.com", "passwd": "$2b$12$VkMtpNJI3z/gUTBBfo45A.1E.y.yRd017FUuIjg6M6PxcJCzkuEZm", "movie_id": 1}, # Nani
    {'id': 4, "name":"Rohit", "email":"Rohit@email.com", "passwd": "$2b$12$e3cRNc/S74CqO5FldqYBhuH9kG92E3If0ANoxNqPxKmVFslNfr3/2", "movie_id": 4}, # Rohit
    {'id': 5, "name":"Vamshi", "email":"Vamshi@email.com", "passwd": "$2b$12$1OGjbQG.Xo5nsXuRkbzqEuFUxLSdlN/Hzj6.vgswFIzuPi9ffqlOe", "movie_id": 5}, # Vamshi
    {'id': 6, "name":"Raju", "email":"Raju@email.com", "passwd": "$2b$12$pggc3xbOmbayiBsLq7ggau.r.9EJGpyzeeYdyPvzXgoY0infXMo9a", "movie_id": 4}, # Raju
    {'id': 7, "name":"Yashwanth", "email":"Yashwanth@email.com", "passwd": "$2b$12$ns.as46M4GfPxS6ajQZF5OREx89vXmlToOVr9CTDejpXTaZuTKmea", "movie_id": 3}, # Yashwanth
    {'id': 8, "name":"Prashanth", "email":"Prashanth@email.com", "passwd": "$2b$12$x31WCZxLz89LTJ410NFmUuLTp18nKtlzUSLuEbiog5KwyOZQ2gQNW", "movie_id": 3}, # Prashanth
    {'id': 9, "name":"Anil", "email":"Anil@email.com", "passwd": "$2b$12$rzFXG6bchpE3PNX6uXVeou0GWReYH3rSikw6FIo1YWoe9X8E2.AVy", "movie_id": 1}, # Anil
    {'id': 10, "name":"Sai Kiran", "email":"Sai.Kiran@email.com", "passwd": "$2b$12$mbDB4cEzx/WXfZQnaMEps.brqSlNhyUMuSoj7lCPtGy37seOh4/wi", "movie_id": 5}, # Sai Kiran
]

# movies = [] # New Movies
# users = [] # New Users

async def get_db():
    db = LocalSession()
    try: 
        yield db
    except Exception as e:
        print("There is a error in database instance: %s" % e)
        raise 
    finally:
        db.close()

def delete_db():
    try:
        db = LocalSession()
        records = db.query(Movies).delete()
        db.commit()
        print(f"Database Instance: {records} Movies records removed!")
    except Exception as e:
        db.rollback()
        print("Database Instance: Movies still Exist's!")
    finally:
        db.close()

def insert_db():
    try:
        db = LocalSession()
        db.add_all([Movies(name=mov['name'], description=mov['description'], released=mov['released']) for mov in movies])
        db.commit()
        records = len(movies)
        print("") if records == 0 else print(f'Database Instance: {records} Movie records added!')
    except Exception as e:
        print("Database Instance: Movies are already Exists!")
    finally:
        db.close()

def delete_users_db():
    try:
        db = LocalSession()
        users = db.query(Users).delete()
        db.commit()
        print(f"Database Instance: {users} Users records removed!")
    except:
        db.rollback()
        print("Database Instance: Users still Exist's!")
    finally:
        db.close()

def insert_users_db():
    try:
        db = LocalSession()
        db.add_all([Users(id=user['id'], name=user['name'], email=user['email'], passwd=user['passwd'], movie_id=user['movie_id']) for user in users])
        db.commit()
        records = len(users)
        print("") if records == 0 else print(f'Database Instance: {records} User records added!')
    except Exception as e:
        print("Database Instance: Users are already Exists!")
    finally:
        db.close()

# No need of overhead / Checking with local and db values are in sync 

# Movies
def add_remove_movies():
    _db = session.query(Movies.id, Movies.name, Movies.description, Movies.released).all()
    _movies = [tuple(mov.values()) for mov in movies]
    if _db != _movies:
        print("<==================Movies======================>")
        delete_db() # Initital Deletion with the local movies by sync
        insert_db() # Initial Insertion with the movies 
    else:
        print("Database Instance: Movies still exist's in local, db and are in Sync!")

# Users
def add_remove_users():
    _users_db = session.query(Users.id, Users.name, Users.email, Users.passwd, Users.movie_id).all()
    _users = [tuple(usr.values()) for usr in users]
    if _users_db != _users:
        print("<===================Users=======================>")
        delete_users_db() # Initial Deletion with local users by sync
        insert_users_db() # Intital Insertion with the users
    else:
        print("Database Instance: Users still exist's in local, db and are in Sync!")