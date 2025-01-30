from app.models.user import User
from app.services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException
from app.utils import verify_password
from sqlalchemy.orm import selectinload


class UserService(BaseService):
    def __init__(self, db):
        super().__init__(db, User)

    async def create(self, user: UserCreate):
        """Create a new user."""
        user = User(**user.to_dict())
        self.db.add(user)
        await self.db.commit()
        print(user.__dict__)
        return user
    
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
