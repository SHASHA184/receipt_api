import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.config import settings
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Создаем синхронный движок для управления БД (PostgreSQL требует синхронных команд CREATE DATABASE)
admin_engine = create_engine(
    str(settings.SYNC_SQLALCHEMY_DATABASE_URL), isolation_level="AUTOCOMMIT"
)

# Асинхронный движок для тестовой базы
engine = create_async_engine(
    str(settings.TEST_SQLALCHEMY_DATABASE_URL), echo=True, poolclass=NullPool
)

# Сессия для тестов
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def create_test_database():
    """Создает тестовую БД, если её нет."""
    with admin_engine.connect() as conn:
        try:
            db_name = str(settings.SYNC_TEST_SQLALCHEMY_DATABASE_URL).rsplit("/", 1)[-1]
            print(f"Creating test database {db_name}")
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        except Exception as e:
            print(f"Database {db_name} already exists, continuing... ({e})")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Пересоздает схему базы перед тестами и удаляет после.
    """
    create_test_database()  # Создаем тестовую БД (синхронно)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляем старые таблицы
        await conn.run_sync(Base.metadata.create_all)  # Создаем новые таблицы

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляем БД после тестов


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(db: AsyncSession):
    """
    Очищает базу данных перед каждым тестом.
    """
    tables = ["users", "receipts", "receipt_items"]
    for table in tables:
        await db.execute(text(f"TRUNCATE {table} RESTART IDENTITY CASCADE;"))
    await db.commit()


@pytest_asyncio.fixture
async def db():
    """
    Предоставляет изолированную сессию БД для тестов.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    """
    Создает FastAPI тестовый клиент с тестовой БД.
    """

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
