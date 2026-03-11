from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ExpenseBase(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    amount: float = Field(..., gt=0)

class ExpenseCreate(ExpenseBase):
    expense_date: Optional[datetime] = None

class ExpenseUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[datetime] = None

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    expense_date: datetime

    model_config = ConfigDict(from_attributes=True)
