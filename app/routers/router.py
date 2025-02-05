from fastapi import APIRouter
from . import auth_router, users_router, categories_router, expenses_router, budgets_router
from ..constants.endpoints import AUTH, USER, CATEGORY, EXPENSE, BUDGET

api_router = APIRouter()
api_router.include_router(auth_router, prefix=AUTH, tags=["auth"])
api_router.include_router(users_router, prefix=USER, tags=["user"])
api_router.include_router(categories_router, prefix=CATEGORY, tags=["category"])
api_router.include_router(expenses_router, prefix=EXPENSE, tags=["expense"])
api_router.include_router(budgets_router, prefix=BUDGET, tags=["budget"])