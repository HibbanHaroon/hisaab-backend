from fastapi import FastAPI
from .routers import auth, users, categories, budget, expense

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(budget.router)
app.include_router(expense.router)

@app.get("/")
async def root():
    return {"info": "Welcome to Hisaab Backend", "docs": "http://127.0.0.1:8000/docs/"}