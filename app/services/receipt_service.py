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
        receipt_data = receipt_create.prepare_receipt_data(owner_id)

        receipt = self.model(**receipt_data)
        self.db.add(receipt)
        await self.db.commit()
        await self.db.refresh(receipt)

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

        receipts_with_items = []
        for receipt in receipts:
            items_query = select(ReceiptItem).filter(ReceiptItem.receipt_id == receipt.id)
            items_result = await self.db.execute(items_query)
            items = items_result.scalars().all()

            products = [
                Product(name=item.name, price=float(item.price), quantity=item.quantity)
                for item in items
            ]

            receipt_schema = Receipt.from_orm_with_items(receipt, products)
            receipts_with_items.append(receipt_schema)

        return receipts_with_items

    async def get_receipt_text(self, receipt_id: int, line_length: int = 40) -> str:
        """Generate a text representation of the receipt."""
        receipt = await self.get(receipt_id)
        items_query = select(ReceiptItem).filter(ReceiptItem.receipt_id == receipt_id)
        items_result = await self.db.execute(items_query)
        items = items_result.scalars().all()

        lines = []
        lines.append("ФОП Джонсонюк Борис".center(line_length))
        lines.append("=" * line_length)

        for item in items:
            price_formatted = f"{item.price:,.2f}".replace(",", " ")
            total_formatted = f"{item.total:,.2f}".replace(",", " ")

            lines.append(f"{item.quantity} x {price_formatted} {total_formatted.rjust(line_length - len(f'{item.quantity} x {price_formatted} '))}")

            lines.append(item.name.ljust(line_length))

        lines.append("=" * line_length)

        total_formatted = f"{receipt.total:,.2f}".replace(",", " ")
        payment_amount_formatted = f"{receipt.payment_amount:,.2f}".replace(",", " ")
        rest_formatted = f"{receipt.rest:,.2f}".replace(",", " ")

        payment_type_translation = {
            "cash": "Готівка",
            "cashless": "Картка",
        }
        
        payment_type = payment_type_translation.get(receipt.payment_type.value, receipt.payment_type.value)

        lines.append(f"СУМА {total_formatted.rjust(line_length - len('СУМА '))}")
        lines.append(f"{payment_type} {payment_amount_formatted.rjust(line_length - len(payment_type) - 1)}")
        lines.append(f"Решта {rest_formatted.rjust(line_length - len('Решта '))}")
        lines.append("=" * line_length)

        lines.append(receipt.created_at.strftime("%d.%m.%Y %H:%M").center(line_length))
        lines.append("Дякуємо за покупку!".center(line_length))

        return "\n".join(lines)