from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.enums.receipt_payment import PaymentType
from pydantic import model_validator, field_validator, Field


class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="The name of the product.")
    price: float = Field(..., gt=0, description="The price of the product.")
    quantity: int = Field(..., gt=0, description="The quantity of the product.")

class Payment(BaseModel):
    type: PaymentType = Field(..., description="The type of payment.")
    amount: float = Field(..., gt=0, description="The payment amount.")

    @field_validator("amount")
    def round_amount(cls, value):
        """Round the payment amount to two decimal places."""
        return round(value, 2)


class ReceiptCreate(BaseModel):
    products: List[Product] = Field(..., min_length=1, description="The list of products.")
    payment: Payment = Field(..., description="The payment information.")

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
    id: int = Field(..., description="The ID of the receipt.")
    total: float = Field(..., description="The total cost of products.")
    rest: float = Field(..., description="The rest (change) based on the payment amount.")
    created_at: datetime = Field(..., description="The date and time of the receipt creation.")
    owner_id: int = Field(..., description="The ID of the receipt owner.")

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
