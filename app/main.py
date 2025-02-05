from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy_utils import database_exists, create_database
import uvicorn

from .db.base import Base, engine
from .routers import auth, users, categories, budget, expense
from .exceptions import CustomHTTPException, http_exception_handler
from .settings import settings

def init_db() -> None:
    """Initialize database and create tables if they don't exist."""
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)

# Register startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application on startup."""
    init_db()
    yield

# TODO: Create a function which returns FastAPI

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)


# TODO: Add these routers in a file routers/router.py
# TODO: Move the routers files to an endpoints folder
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(budget.router)
app.include_router(expense.router)

app.add_exception_handler(CustomHTTPException, http_exception_handler)

@app.get("/")
async def root():
    return {"info": "Welcome to Hisaab Backend"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, workers=1)