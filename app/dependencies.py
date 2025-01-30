from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.utils import decode_access_token
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """Retrieve the current authenticated user.

    This function decodes the access token to retrieve the user ID,
    then fetches the user from the database using the user ID.
    """
    payload = decode_access_token(token)
    id: str = payload.get("sub")
    if not id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user_service = UserService(db)

    user = await user_service.get(int(id))
    return user
