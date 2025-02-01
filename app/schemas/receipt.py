from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.enums.receipt_payment import PaymentType
from pydantic import model_validator, field_validator


class Product(BaseModel):
    name: str
    price: float
    quantity: int

    @field_validator("price")
    def validate_price(cls, value):
        """Validate that the product price is greater than zero."""
        if value <= 0:
            raise ValueError("The product price must be greater than zero.")
        
        return value
    
    @field_validator("quantity")
    def validate_quantity(cls, value):
        """Validate that the product quantity is greater than zero."""
        if value <= 0:
            raise ValueError("The product quantity must be greater than zero.")
        
        return value


class Payment(BaseModel):
    type: PaymentType
    amount: float

    @field_validator("amount")
    def round_amount(cls, value):
        """Round the payment amount to two decimal places."""
        return round(value, 2)


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

    @model_validator(mode="after")
    def validate_payment_amount(self):
        """Validate that the payment amount is not less than the total cost of products."""

        if self.payment.amount < self.total:
            raise ValueError(
                "The payment amount cannot be less than the total cost of products."
            )
        
        return self

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
