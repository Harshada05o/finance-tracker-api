from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# ---- Category schemas ----
class CategoryBase(BaseModel):
    name: str
    type: str  # "income" or "expense"

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# ---- Transaction schemas ----
class TransactionBase(BaseModel):
    amount: Decimal
    note: Optional[str] = None
    date: date
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    category: CategoryOut

    class Config:
        from_attributes = True