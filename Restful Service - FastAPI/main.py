import os
import sys
# from ...TRAINING.repository import movie | ImportError: attempted relative import beyond top-level package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request
from routers import Movies_, Users_, Authentication_

from fastapi.responses import HTMLResponse
import uvicorn

from databases import engine, add_remove_movies, add_remove_users
from models import Base

# FastAPI Instances
app = FastAPI(title='API Testing')
app.include_router(Authentication_.router)
app.include_router(Movies_.router)
app.include_router(Users_.router)


# Database Instances
Base.metadata.create_all(bind=engine) # migration of the tables
add_remove_movies()
add_remove_users()


# Index Page
@app.get('/')
async def index(request: Request):
    return HTMLResponse("""
    <html>
    <body>
        <!-- <h1>API Testing</h1> -->
        <nav>
            <a href="/movies/" method="GET">List of Movies</a>
            <!--
            <a href="/movies/" method="POST">Add Movies</a>
            <a href="/movies/" method="PUT">Edit Movies</a>
            <a href="/movies/" method="DELETE">Delete Movies</a>
            -->
        </nav>
    </body>
    </html>
    """)
    # redirect_url = request.url_for('/movies/')
    # return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    uvicorn.run(app, reload=True, host='127.0.0.1', port=8080) # uvicorn main:app --reload