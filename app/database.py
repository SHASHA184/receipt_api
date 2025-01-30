from typing import AsyncGenerator
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy.ext.declarative import declarative_base


engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URL), future=True, echo=False)

sync_engine = create_engine(str(settings.SYNC_SQLALCHEMY_DATABASE_URL), future=True, echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

sync_session = sessionmaker(sync_engine, expire_on_commit=False)

Base = declarative_base()


# Dependency
async def get_db() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as sql_ex:
            await session.rollback()
            raise sql_ex
        except HTTPException as http_ex:
            await session.rollback()
            raise http_ex
        finally:
            await session.close()


def get_sync_db():
    session = sync_session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as sql_ex:
        session.rollback()
        raise sql_ex
    except HTTPException as http_ex:
        session.rollback()
        raise http_ex
    finally:
        session.close()