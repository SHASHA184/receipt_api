from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.receipt import ReceiptCreate, Receipt
from app.services.receipt_service import ReceiptService
from app.dependencies import get_db, get_current_user
from app.schemas.user import User
from typing import List, Optional
from datetime import datetime
from app.enums.receipt_payment import PaymentType
from fastapi.responses import Response

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
)


@router.post("/", response_model=Receipt)
async def create_receipt(
    receipt_create: ReceiptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    receipt_service = ReceiptService(db)
    receipt = await receipt_service.create(receipt_create, current_user.id)
    return receipt


@router.get("/", response_model=List[Receipt])
async def get_receipts(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    payment_type: Optional[PaymentType] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt_service = ReceiptService(db)
    receipts = await receipt_service.get_by_owner(
        current_user.id,
        start_date,
        end_date,
        min_total,
        max_total,
        payment_type,
        limit,
        offset,
    )
    return receipts


@router.get("/{receipt_id}/text")
async def get_receipt_text(
    receipt_id: int, line_length: int = 40, db: AsyncSession = Depends(get_db)
):
    """Get a receipt in text format by its ID."""
    receipt_service = ReceiptService(db)
    receipt_text = await receipt_service.get_receipt_text(receipt_id, line_length)
    return Response(content=receipt_text, media_type="text/plain")