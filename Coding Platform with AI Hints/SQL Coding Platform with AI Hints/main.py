import os 
import re
import sys
# from ...TRAINING.repository import movie | ImportError: attempted relative import beyond top-level package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from itertools import zip_longest
from fastapi import FastAPI, Request, Depends, status, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from typing import Optional, List
from routers import Authentication, Users

from hints import analyze_query_with_langchain, generate_agentic_hints, generate_chain_of_thought, analyze_and_improve_questions, llm_generate_questions
from databases import app_lifespan, get_mysql_db, get_sqlite_db, sqlite_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError, OperationalError, IntegrityError
from sqlalchemy import text, func
from schemas import QuestionSubmission, HintsDescription, QuestionGeneration
from models import Base, CodingQuestions
from sanitize import sanitize_html, sanitize_input
from tokens import get_current_user
import cssutils
import logging

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='SQL Coding Platform with AI Hints', lifespan=app_lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

# routes
app.include_router(Authentication.router)
app.include_router(Users.router)

# middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Specify the correct frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specify only the methods your API uses
    allow_headers=["Authorization", "Content-Type"],  # Ensure 'Authorization' is allowed for JWT tokens
)
"""
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, but you should limit this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
"""

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Get a logger instance for your module
cssutils.log.setLevel(logging.CRITICAL)  # To silence cssutils warnings if necessary

# Database Instances
Base.metadata.create_all(bind=sqlite_engine)

@app.get("/", tags=['Authentication'])
async def login_page(request: Request):
    # Render the 'login.html' template
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/questions-list", tags=['frontend'])
async def list_questions(request: Request, db: Session = Depends(get_sqlite_db), page: Optional[int] = 1, page_size: Optional[int] = 1):
    """return the creating questions page for the admin to create sql questions"""
    """Need to create | update | delete buttons"""
    # Calculate offset
    skip = (page - 1) * page_size

    # Fetch paginated items
    query = select(CodingQuestions).offset(skip).limit(page_size)
    result = db.execute(query)
    items = result.scalars().all()

    # Determine total number of pages
    total_items_query = select(func.count(CodingQuestions.ID))
    total_items = db.execute(total_items_query).scalar_one()
    total_pages = (total_items + page_size - 1) // page_size

    return templates.TemplateResponse("questions.html", {
        "request": request,
        "items": items,
        "total_pages": total_pages,
        "current_page": page
    })

@app.get('/question/{id}', response_class=HTMLResponse, status_code=status.HTTP_200_OK, tags=['frontend'])
async def get_question(request: Request, id: int, db_sqlite: Session = Depends(get_sqlite_db), db_mysql: Session = Depends(get_mysql_db)):
    """Fetch and return the specific question from the database."""
    question = db_sqlite.query(CodingQuestions).filter(CodingQuestions.ID == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # fetch the first 5 records of the data
    # Check if the database schema file exists
    try:
        schema_file_path = f"Sessions/Schemas/{question.DatabaseSchema}"
        # print("Fetched: ", schema_file_path)
        if not os.path.exists(schema_file_path):
            raise HTTPException(status_code=404, detail="Database schema file not found")
        
        database_schema = open(schema_file_path, 'r').read()
        tables = set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(?:\w+\.)?(\w+)", database_schema, re.IGNORECASE))
        
        data = []
        for table in tables:
            # Ensure safe handling of table names, consider using a more secure method for dynamic table names
            query = text(f'SELECT * FROM {table} LIMIT 5;')
            result = await db_mysql.execute(query)  # Make sure this is awaited
            results = result.fetchall() if result.returns_rows else []
            results_list = [row._asdict() for row in results]
            assert results_list not in (None, [])
            results_list = results_list[::-1]  if len(results_list[0]) <= 2 else results_list
            data.append((table, results_list))
    except Exception as e:
        print(f"Error in Fetching: {e}")

    # remove the sample_solution from the question
    """Converts an SQLAlchemy model instance into a dictionary."""
    question_dict = {} if not question else {c.key: getattr(question, c.key) for c in question.__table__.columns}
    question_dict.pop('SampleSolution', None)  # Remove the SampleSolution key
    
    # Assuming you want to pass the question object directly to your template.
    # You might need to adjust the template to handle this object properly.
    return templates.TemplateResponse('questionSolve.html', {'request': request, 'question': question, 'data': data})

@app.post("/test-sql-query", tags=['frontend'])
async def test_sql_query(request: Request, db_mysql: AsyncSession = Depends(get_mysql_db), db_sqlite: Session = Depends(get_sqlite_db), current_user = Depends(get_current_user)):
    body = await request.json()
    query = body.get("query")
    schema_filename = body.get('databaseSchemaFilename')  # Assuming this is passed from the frontend
    embed_code = body.get("embedCode")

    # Fetch database_schema from file
    schema_path = f"Sessions/Schemas/{schema_filename}"
    if not os.path.exists(schema_path):
        return JSONResponse(status_code=404, content={"error": "Database schema file not found."})
    
    with open(schema_path, 'r') as file:
        database_schema = file.read()

    if not query or not schema_filename:
        raise HTTPException(status_code=400, detail="No SQL query provided")
    
    # Extract table names from database_schema
    tables_defined = set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(?:\w+\.)?(\w+)", database_schema, re.IGNORECASE))

    # Initialize a flag to track if schema needs execution
    schema_needed = False

    # Check if each table exists, mark schema_needed as True if any table is missing
    for table_name in tables_defined:
        table_exists_query = await db_mysql.execute(text(f"SHOW TABLES LIKE '{table_name}';"))
        if table_exists_query.first() is None:
            schema_needed = True
            break

    # Extract table names referenced in sample_solution
    tables_referenced = set(re.findall(r"FROM\s+(\w+)", query, re.IGNORECASE))

    # Validate if sample_solution references only tables from database_schema
    if not tables_referenced.issubset(tables_defined):
        missing_tables = tables_referenced - tables_defined
        error_message = f"Sample Solution referenced tables not defined in Database Schema: {', '.join(missing_tables)}."
        return JSONResponse(status_code=400, content={"error": f"{error_message}"})
    
    # Execute database_schema if needed
    if schema_needed:
        try:
            await db_mysql.execute(text(database_schema))
        except (ProgrammingError, OperationalError) as e:
            error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
            match = re.search(r"\(pymysql.err.\w+\) \(\d+, \"([^\"]+)\"\)", error_info)
            if match:
                user_friendly_error = match.group(1)
            else:
                # Extract and simplify the error message
                match = re.search(r"\(.*?\)\s+\((\d+),\s*\"([^\"]+)\"\)", str(e))
                error_message = str(e) if not match else match.group(2)
                user_friendly_error = "An error occurred while processing your Database Schema. Please check your syntax."
                return JSONResponse(status_code=400, content={"error": f"{user_friendly_error} {error_message}"})
            return JSONResponse(status_code=400, content={"error": f"{user_friendly_error} {error_info}"})

    try:
        # Execute the query and fetch results
        # Use `text()` for the raw SQL query to ensure it is safely executed
        result = await db_mysql.execute(text(query))
        results = result.fetchall() if result.returns_rows else [] # Use `scalars().all()` to fetch results
        results_list = [row._asdict() for row in results] # dict(row) instead of row._asdict() 

        # Fetch the sample solution which is expected to be a SQL query
        sample_solution = db_sqlite.query(CodingQuestions.SampleSolution).filter(CodingQuestions.ID == embed_code).first()
        if not sample_solution:
            return JSONResponse(status_code=400, content={"error": "Solution not found."})

        # Execute the sample solution query
        sample_result = await db_mysql.execute(text(sample_solution.SampleSolution))
        sample_results = [row._asdict() for row in sample_result.fetchall()] if sample_result.returns_rows else []

        # Compare row counts
        user_row_count = len(results_list)
        expected_row_count = len(sample_results)
        
        assert results_list not in (None, [])
        assert sample_results not in (None, [])

        # Compare values 
        status_success_error = "success" if all([i==j for i,j in zip_longest(sample_results, results_list)]) else "error"
        # print(status_success_error)

        # reduce the web page load in return the values
        results_list = results_list[::-1]  if len(results_list[0]) <= 2 else results_list   
        sample_results = sample_results[::-1]  if len(sample_results[0]) <= 2 else sample_results   
        
        return {"status": status_success_error, "userData": results_list[:5], "expectedData": sample_results[:5],  "Output": f"{user_row_count} rows", "ExpectedOutput": f"{expected_row_count} rows"}
    except (SQLAlchemyError, Exception, ProgrammingError, OperationalError) as e:
        await db_mysql.rollback()  # Rollback in case of exception
        error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
        match = re.search(r"\(pymysql.err.\w+\) \(\d+, \"([^\"]+)\"\)", error_info)
        if match:
            user_friendly_error = match.group(1)
        else:
            # Extract and simplify the error message
            match = re.search(r"\(.*?\)\s+\((\d+),\s*\"([^\"]+)\"\)", str(e))
            error_message = str(e) if not match else match.group(2)
            user_friendly_error = "An error occurred while processing your query. Please check your syntax."
            return JSONResponse(status_code=400, content={"error": f"{user_friendly_error} {error_message}"})
        return JSONResponse(status_code=400, content={"error": f"{user_friendly_error} {error_info}"})

@app.get('/create-question', response_class=HTMLResponse, status_code=status.HTTP_200_OK, tags=['backend'])
async def create_content(request: Request):
    """return the list of schema files present in our persistent storage"""
    schema_folder = "Sessions/Schemas/"
    files = [f for f in os.listdir(schema_folder) if os.path.isfile(os.path.join(schema_folder, f)) and f.endswith('.sql')]
    return templates.TemplateResponse("content.html", context={'request': request, "schema_files": files})


# Schema File names from the Local "Session/Schemas" Folder
@app.get("/schema-content/{fileName}", tags=['backend'])
async def get_schema_content(fileName: str):
    """fetch the schema file contents"""
    file_path = f"Sessions/Schemas/{fileName}"
    if os.path.exists(file_path) and fileName.endswith('.sql'):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Backend Testing while creating the question
@app.post("/test-query", tags=['backend'])
async def test_query(request: Request, db: AsyncSession = Depends(get_mysql_db), current_user = Depends(get_current_user)):
    data = await request.json()
    database_schema = data.get("database_schema")
    sample_solution = data.get("sample_solution")

    # Validate input
    if not database_schema or not sample_solution:
        detail = "Test Failed: "
        detail += "Database schema is required. " if not database_schema else ""
        detail += "Sample solution is required." if not sample_solution else ""
        raise HTTPException(status_code=400, detail=detail)

    # Extract table names from database_schema
    tables_defined = set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(?:\w+\.)?(\w+)", database_schema, re.IGNORECASE))

    # Initialize a flag to track if schema needs execution
    schema_needed = False

    # Check if each table exists, mark schema_needed as True if any table is missing
    for table_name in tables_defined:
        table_exists_query = await db.execute(text(f"SHOW TABLES LIKE '{table_name}';"))
        if table_exists_query.first() is None:
            schema_needed = True
            break

    # Extract table names referenced in sample_solution
    tables_referenced = set(re.findall(r"FROM\s+(\w+)", sample_solution, re.IGNORECASE))

    # Validate if sample_solution references only tables from database_schema
    if not tables_referenced.issubset(tables_defined):
        missing_tables = tables_referenced - tables_defined
        error_message = f"Sample Solution referenced tables not defined in Database Schema: {', '.join(missing_tables)}."
        return JSONResponse(status_code=400, content={"error": f"Test Failed: {error_message}"})
    
    # Execute database_schema if needed
    if schema_needed:
        try:
            await db.execute(text(database_schema))
        except (ProgrammingError, OperationalError) as e:
            error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
            match = re.search(r"\(pymysql.err.\w+\) \(\d+, \"([^\"]+)\"\)", error_info)
            if match:
                user_friendly_error = match.group(1)
            else:
                # Extract and simplify the error message
                match = re.search(r"\(.*?\)\s+\((\d+),\s*\"([^\"]+)\"\)", str(e))
                error_message = str(e) if not match else match.group(2)
                user_friendly_error = "An error occurred while processing your Database Schema. Please check your syntax."
                return JSONResponse(status_code=400, content={"error": f"Test Failed: {user_friendly_error} {error_message}"})
            return JSONResponse(status_code=400, content={"error": f"Test Failed: {user_friendly_error} {error_info}"})

    # Proceed with executing sample_solution
    try:
        result = await db.execute(text(sample_solution))
        try:
            results = result.fetchall() if result.returns_rows else []
            results_list = [row._asdict() for row in results]
            assert results_list not in (None, [])
            await db.commit()
            results_list = results_list[::-1]  if len(results_list[0]) <= 2 else results_list
            return JSONResponse(content={"results": results_list[:10]})
        except Exception as e:
            await db.rollback()
            # Extract and simplify the error message
            match = re.search(r"\(.*?\)\s+\((\d+),\s*\"([^\"]+)\"\)", str(e))
            error_message = str(e) if not match else match.group(2)
            user_friendly_error = "An error occurred while processing your Database Schema. Please check your syntax."
            return JSONResponse(status_code=400, content={"error": f"Test Failed: {user_friendly_error} {error_message}"})
    except (ProgrammingError, OperationalError) as e:
        await db.rollback()
        # Handle sample_solution errors similarly
        error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
        match = re.search(r"\(pymysql.err.\w+\) \(\d+, \"([^\"]+)\"\)", error_info)
        if match:
            user_friendly_error = match.group(1)
        else:
            # Extract and simplify the error message
            match = re.search(r"\(.*?\)\s+\((\d+),\s*\"([^\"]+)\"\)", str(e))
            error_message = str(e) if not match else match.group(2)
            user_friendly_error = "An error occurred while processing your Sample Solution SQL. Please check your syntax."
            return JSONResponse(status_code=400, content={"error": f"Test Failed: {user_friendly_error} {error_message}"})
        return JSONResponse(status_code=400, content={"error": f"Test Failed: {user_friendly_error} {error_info}"})


@app.post("/submit-question", tags=['backend'])
async def submit_question(question: QuestionSubmission, db: Session = Depends(get_sqlite_db), current_user = Depends(get_current_user)):
    # If fileName is not provided, use "new_schema" as default
    raw_file_name = question.fileName if question.fileName else "new_schema"
    
    # Normalize file name by removing .sql extension if present
    normalized_file_name = raw_file_name[:-4] if raw_file_name.lower().endswith('.sql') else raw_file_name
    
    # Sanitize fileName to remove invalid filesystem characters
    allowed_pattern = re.compile(r"[^a-zA-Z0-9_-]")
    sanitized_file_name = allowed_pattern.sub("", normalized_file_name)
    
    # Ensure the file name ends with .sql
    final_file_name = sanitized_file_name + '.sql'
    
    schema_file_path = f"Sessions/Schemas/{final_file_name}"
    
    # Create directories if not exists
    os.makedirs(os.path.dirname(schema_file_path), exist_ok=True)
    
    # Check if the file already exists
    if not os.path.exists(schema_file_path):
        print(f"File Created: '{schema_file_path}'")
        # Create new schema file if it doesn't exist
        with open(schema_file_path, 'w') as f:
            f.write(question.databaseSchema)

    # Sanitize the input HTML
    safe_html = sanitize_html(question.description)
        
    # Logic for MySQL and SQLite operations
    try:
        # Create a new CodingQuestions instance with the data
        new_question = CodingQuestions(
            Title=question.title,
            Description=safe_html,
            Difficulty=question.difficultLevel,
            DatabaseSchema=final_file_name, # Assuming you want to store the file name/path
            UserQuery=question.userQuery,
            SampleSolution=question.sampleSolution,
        )
        # Add the new question to the session and commit it to the database
        db.add(new_question)
        db.commit()

        # After committing, you can return the ID of the new question, if needed
        db.refresh(new_question)
        return RedirectResponse(url="/questions-list", status_code=status.HTTP_303_SEE_OTHER)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        if "UNIQUE constraint failed" in str(e.orig):
            # Correctly raise an HTTPException
            raise HTTPException(status_code=400, detail=f"Question with the title '{question.title}' already exists.")
        else:
            raise HTTPException(status_code=400, detail="A database error occurred.")
    except Exception as e:
        db.rollback()  # Ensure rollback on generic exception
        logger.error(f"Unexpected error: {e}")
        # For other unexpected errors, you may choose to log the error and raise a generic HTTPException
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
    finally:
        db.close()  # Ensure DB connection is always closed


@app.post("/get-hints", response_model=dict, tags=['frontend'])
async def get_hints(hints_description: HintsDescription, db_sqlite: Session = Depends(get_sqlite_db), current_user = Depends(get_current_user)):
    """Fetch and return the specific question from the database."""
    question = db_sqlite.query(CodingQuestions).filter(CodingQuestions.ID == hints_description.embedCode).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if the database schema file exists
    schema_file_path = f"Sessions/Schemas/{question.DatabaseSchema}"
    if not os.path.exists(schema_file_path):
        raise HTTPException(status_code=404, detail="Database schema file not found")
    
    with open(schema_file_path, 'r') as file:
        database_schema = file.read()
        
    # Assume analyze_query_with_langchain returns a structured analysis
    analysis = analyze_query_with_langchain(hints_description.userQuery, question.Description, database_schema)
    
    # print(f"invoked: {hints_description}")
    
    # Generate hints based on the analysis
    # hints = generate_agentic_hints(analysis) or generate_chain_of_thought(analysis)

    if not analysis['feedback']:
        raise HTTPException(status_code=404, detail="No hints could be generated.")

    return {"hints": analysis['feedback']} 

@app.get('/generate')
async def generate(request: Request):
    return templates.TemplateResponse("questionGenerate.html", {"request": request})


@app.post("/generate-questions")
async def generate_questions_list(request: QuestionGeneration, current_user = Depends(get_current_user)):
    # Generate questions using the LLM
    generated_questions = await llm_generate_questions(request)  # Adjust this call based on your LLM wrapper's interface
    print(generated_questions)
    
    # Analyze and improve the generated questions
    improved_questions = await analyze_and_improve_questions(generated_questions)

    return {"data": improved_questions}  # Adjust this response as needed for your front-end
