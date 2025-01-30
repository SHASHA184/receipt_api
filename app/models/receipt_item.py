from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(DECIMAL(10, 2))
    quantity = Column(Integer)
    total = Column(DECIMAL(10, 2))
    receipt_id = Column(Integer, ForeignKey("receipts.id"))

    receipt = relationship("Receipt", back_populates="items")