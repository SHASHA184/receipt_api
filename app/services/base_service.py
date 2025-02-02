from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import EntityNotFoundException
from sqlalchemy.future import select
from pydantic import BaseModel


class BaseService(ABC):
    def __init__(self, db: AsyncSession, model):
        """
        Base service class for CRUD operations.
        Attributes:
            db (AsyncSession): Async SQLAlchemy session.
            model: SQLAlchemy model.
        """
        self.db = db
        self.model = model


    async def get(self, id: int):
        """
        Get a single entity by ID.
        Args:
            id (int): Entity ID.
        Returns:
            SQLAlchemy model instance.
        """
        return await self.get_entity_or_404(self.model, id)

    async def get_entity_or_404(self, model, id, options=None):
        """
        Get an entity by ID or raise a 404 error if it doesn't exist.
        Args:
            model: SQLAlchemy model.
            id (int): Entity ID.
            options: Опции загрузки отношений.
        Returns:
            SQLAlchemy model instance.
        Raises:
            EntityNotFoundException: If the entity doesn't exist.
        """
        query = select(model).filter(model.id == id)
        if options:
            query = query.options(*options)
        result = await self.db.execute(query)
        entity = result.scalars().first()
        if entity is None:
            raise EntityNotFoundException(model.__name__)
        return entity

    async def create(self, obj: BaseModel):
        """
        Create an entity.
        Args:
            obj: Pydantic model instance with entity data.
        Returns:
            SQLAlchemy model instance.
        """
        entity = self.model(**obj.model_dump())
        self.db.add(entity)
        await self.db.commit()
        return entity

    async def update(self, id: int, obj: BaseModel):
        """
        Update an entity.
        Args:
            id (int): Entity ID.
            obj: SQLAlchemy model instance with updated data.
        Returns:
            SQLAlchemy model instance.
        """
        entity = await self.get_entity_or_404(self.model, id)
        for key, value in obj.model_dump(exclude_none=True).items():
            setattr(entity, key, value)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity


    async def delete(self, id: int):
        """Delete an entity."""
        entity = await self.get_entity_or_404(self.model, id)
        self.db.delete(entity)
        await self.db.commit()
        return entity
