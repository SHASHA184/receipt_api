from app.models.user import User
from app.services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.utils import verify_password
from sqlalchemy.orm import selectinload


class UserService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def create(self, user: UserCreate):
        """Create a new user."""
        user = User(**user.to_dict())
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError as e:
            await self.db.rollback()
            if "unique constraint" in str(e.orig):
                raise HTTPException(status_code=400, detail="User with this email already exists")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update(self, id, user_update: UserUpdate):
        """Update a user."""
        entity = await self.get_entity_or_404(self.model, id)
        update_data = user_update.to_dict()

        for key, value in update_data.items():
            setattr(entity, key, value)

        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def authenticate_user(self, db: AsyncSession, username: str, password: str):
        """Authenticate a user by username and password."""
        query = select(User).filter(User.username == username)
        user = await db.execute(query)
        user = user.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
        return user
