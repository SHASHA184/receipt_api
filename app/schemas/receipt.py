from pydantic import BaseModel
from typing import List
from datetime import datetime


class Product(BaseModel):
    name: str
    price: float
    quantity: int


class Payment(BaseModel):
    type: str
    amount: float


class ReceiptCreate(BaseModel):
    products: List[Product]
    payment: Payment


class Receipt(ReceiptCreate):
    id: int
    total: float
    rest: float
    created_at: datetime
    owner_id: int
