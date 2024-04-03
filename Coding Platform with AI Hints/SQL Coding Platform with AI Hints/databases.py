import os
import re
from dotenv import load_dotenv, find_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from models import Base
from sqlalchemy import create_engine 
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from typing import List

load_dotenv(find_dotenv(), override=True)


# SQLite for storing objects and Create sync engine for SQLite and Create sessionmaker
SQLITE_DATABASE_URL = "sqlite:///Sessions/codingquesitons.sqlite3"  # Example SQLite URL
sqlite_engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}) # only for sqlite3
SyncSessionLocalSQLite = sessionmaker(bind=sqlite_engine, autocommit=False, autoflush=False) # , expire_on_commit=False

# MySQL for testing solutions and Create async engine for MySQL and Create sessionmaker
MYSQL_DATABASE_URL = os.getenv("MYSQL_DATABASE_URL")  # Assumes MYSQL_DATABASE_URL is in your .env file
mysql_engine = create_async_engine(MYSQL_DATABASE_URL) # , echo=True, future=True
AsyncSessionLocalMySQL = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine, class_=AsyncSession, expire_on_commit=False)


# Dependency for SQLite sessions
def get_sqlite_db():
    """Dependency that provides a session for synchronous SQLite operations, run in a background thread."""
    db = SyncSessionLocalSQLite()
    try:
        yield db
    except Exception as e:
        print("There is a sqlite db error: %s" %e)
        raise
    finally:
        db.close()

# Dependency for MySQL sessions
async def get_mysql_db():
    try:
        async with AsyncSessionLocalMySQL() as session:
            yield session
    except Exception as e:
        print("There is a mysql db error: %s" %e)
        raise

# Assuming create_tables is an asynchronous function that should be awaited
async def create_tables(engine: AsyncEngine):
    """Asynchronously create tables based on metadata if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Assuming dispose_engine is defined as an async function:
async def dispose_engine(engine: AsyncEngine):
    """Asynchronously dispose of the given SQLAlchemy engine."""
    await engine.dispose()
    
def dispose_sqlite_engine(engine):
    """Synchronously dispose of the given SQLAlchemy SQLite engine."""
    engine.dispose()

# Correctly structured lifespan handler
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI to manage startup and shutdown events."""
    # Startup logic here
    # await create_tables(mysql_engine)
    yield  # Separating startup from shutdown logic
    # Shutdown logic follows
    await dispose_engine(mysql_engine)
    dispose_sqlite_engine(sqlite_engine)  # Dispose of SQLite engine


# ======== Testing =========== #
async def mysql_execute_statements(db: AsyncSession, statements: List[str]):
    try:
        async with db.begin():
            for statement in statements:
                await db.execute(statement)
            await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# =========== Handling the database_schema: DDL ============ #
async def extract_table_name(database_schema):
    # This regex assumes table name follows "CREATE TABLE" (possibly with IF NOT EXISTS) and may not cover all SQL dialects
    match = re.search(r"CREATE TABLE (IF NOT EXISTS )?(IF EXISTS )?(\w+)", database_schema, re.IGNORECASE)
    if match:
        return match.group(3)  # The third group should be the table name
    return None


async def table_exists(db: AsyncSession, table_name: str) -> bool:
    async with db.begin() as transaction:
        # Here we use a raw SQL statement because we're inspecting the database's meta-information
        result = await transaction.connection.execute(text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :table_name)"), {'table_name': table_name})
        exists = await result.scalar()
    return bool(exists)

async def execute_schema_if_not_exists(db: AsyncSession, database_schema: str):
    table_name = await extract_table_name(database_schema)
    if table_name:
        if not await table_exists(db, table_name):
            try:
                await db.execute(text(database_schema))
                await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"Error executing schema: {e}")

async def execute_sample_solution_and_return_results(db, sample_solution):
    try:
        result = await db.execute(text(sample_solution))
        # Assuming result is a SELECT query or similar that fetches rows
        results = result.mappings().all()  # Use .mappings().all() to fetch result rows as dictionaries
        return results
    except SQLAlchemyError as e:
        # Handle error, possibly returning an error message to the frontend
        print(f"Error executing sample solution: {e}")
        return {"error": str(e)}

async def format_sql_error(e):
    error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
    match = re.search(r"\(pymysql.err.\w+\) \(\d+, \"([^\"]+)\"\)", error_info)
    if match:
        return f"SQL Error {match.group(1)}: {match.group(2)}"
    return "An SQL error occurred."


"""
# ================== MySQL ===================== #
# Link: https://www.hostinger.in/tutorials/mysql/how-create-mysql-user-and-grant-permissions-command-line
# Creating User Credentials
CREATE USER 'local_user'@'localhost' IDENTIFIED BY 'password';

# In order to grant all privileges of the database for a newly created user, execute the following command:
GRANT ALL PRIVILEGES ON * . * TO 'new_user'@'localhost';  

# For changes to take effect immediately flush these privileges by typing in the command:
FLUSH PRIVILEGES; 

# To know the column names
select column_name from information_schema.columns where table_name='users';
"""