from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums.receipt_payment import PaymentType


class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    total = Column(DECIMAL(10, 2))
    rest = Column(DECIMAL(10, 2))
    payment_type = Column(Enum(PaymentType))
    payment_amount = Column(DECIMAL(10, 2))
    created_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt")