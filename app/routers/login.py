from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.utils import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService

router = APIRouter(
    tags=["login"],
)


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Authenticate a user and return an access token."""
    user_service = UserService(db)
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

