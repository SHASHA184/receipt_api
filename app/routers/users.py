from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate, User
from app.services.user_service import UserService
from app.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=User)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    return await user_service.create(user_create)


@router.patch("/{id}", response_model=User)
async def update_user(
    id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.update(id, user_update)