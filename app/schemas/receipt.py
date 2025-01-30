from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.enums.receipt_payment import PaymentType


class Product(BaseModel):
    name: str
    price: float
    quantity: int


class Payment(BaseModel):
    type: PaymentType
    amount: float


class ReceiptCreate(BaseModel):
    products: List[Product]
    payment: Payment

    @property
    def total(self) -> float:
        """Calculate the total cost of all products in the receipt."""
        return sum(item.price * item.quantity for item in self.products)

    @property
    def rest(self) -> float:
        """Calculate the rest (change) based on the payment amount."""
        return self.payment.amount - self.total

    def prepare_receipt_data(self, owner_id: int) -> dict:
        """Prepare the data for creating a Receipt model."""
        return {
            "owner_id": owner_id,
            "created_at": datetime.utcnow(),
            "total": self.total,
            "rest": self.rest,
            "payment_type": self.payment.type,
            "payment_amount": self.payment.amount,
        }


class Receipt(ReceiptCreate):
    id: int
    total: float
    rest: float
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_items(cls, receipt, products):
        """Create a Receipt schema from ORM model with products."""
        return cls(
            id=receipt.id,
            total=receipt.total,
            rest=receipt.rest,
            payment_type=receipt.payment_type,
            payment_amount=receipt.payment_amount,
            created_at=receipt.created_at,
            owner_id=receipt.owner_id,
            products=products,
            payment=Payment(type=receipt.payment_type, amount=receipt.payment_amount),
        )
