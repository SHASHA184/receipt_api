# app/services/receipt_service.py
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.receipt import Receipt as ReceiptModel
from app.models.receipt_item import ReceiptItem
from app.schemas.receipt import ReceiptCreate, Product, Receipt
from app.enums.receipt_payment import PaymentType
from app.services.base_service import BaseService
from typing import List, Optional


class ReceiptService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ReceiptModel)

    async def create(self, receipt_create: ReceiptCreate, owner_id: int):
        """Create a new receipt."""
        # Prepare receipt data using the schema method
        receipt_data = receipt_create.prepare_receipt_data(owner_id)

        # Create the receipt
        receipt = self.model(**receipt_data)
        self.db.add(receipt)
        await self.db.commit()
        await self.db.refresh(receipt)

        # Add receipt items
        for item in receipt_create.products:
            receipt_item = ReceiptItem(
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                total=item.price * item.quantity,
                receipt_id=receipt.id,
            )
            self.db.add(receipt_item)
        await self.db.commit()

        return {
            "id": receipt.id,
            "products": [
                {
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "total": item.price * item.quantity,
                }
                for item in receipt_create.products
            ],
            "payment": receipt_create.payment.model_dump(),
            "total": receipt_data["total"],
            "rest": receipt_data["rest"],
            "created_at": receipt_data["created_at"],
            "owner_id": owner_id,
        }

    async def get_by_owner(
        self,
        owner_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_total: Optional[float] = None,
        max_total: Optional[float] = None,
        payment_type: Optional[PaymentType] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ReceiptModel]:
        """Get all receipts belonging to a specific user with optional filters."""
        query = select(ReceiptModel).filter(ReceiptModel.owner_id == owner_id)

        if start_date:
            query = query.filter(ReceiptModel.created_at >= start_date)
        if end_date:
            query = query.filter(ReceiptModel.created_at <= end_date)
        if min_total:
            query = query.filter(ReceiptModel.total >= min_total)
        if max_total:
            query = query.filter(ReceiptModel.total <= max_total)
        if payment_type:
            query = query.filter(ReceiptModel.payment_type == payment_type)

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        receipts = result.scalars().all()

        # Для кожного чеку отримуємо товари
        receipts_with_items = []
        for receipt in receipts:
            items_query = select(ReceiptItem).filter(ReceiptItem.receipt_id == receipt.id)
            items_result = await self.db.execute(items_query)
            items = items_result.scalars().all()

            # Перетворюємо товари в схему Product
            products = [
                Product(name=item.name, price=float(item.price), quantity=item.quantity)
                for item in items
            ]

            # Створюємо схему ReceiptModel з товарами
            receipt_schema = Receipt.from_orm_with_items(receipt, products)
            receipts_with_items.append(receipt_schema)

        return receipts_with_items