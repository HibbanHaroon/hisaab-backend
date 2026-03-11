from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class BudgetBase(BaseModel):
    category_id: int
    total_amount: float = Field(..., gt=0)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    total_amount: Optional[float] = Field(None, gt=0)

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    amount_spent: float = 0.0
    amount_left: float = 0.0

    model_config = ConfigDict(from_attributes=True)
