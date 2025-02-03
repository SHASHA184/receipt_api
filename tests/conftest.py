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

# Create a synchronous engine for database management (PostgreSQL requires synchronous CREATE DATABASE commands)
admin_engine = create_engine(
    str(settings.SYNC_SQLALCHEMY_DATABASE_URL), isolation_level="AUTOCOMMIT"
)

# Asynchronous engine for the test database
engine = create_async_engine(
    str(settings.TEST_SQLALCHEMY_DATABASE_URL), echo=True, poolclass=NullPool
)

# Session for tests
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def create_test_database():
    """Creates a test database if it does not exist."""
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
    Recreates the database schema before tests and deletes it after.
    """
    create_test_database()  # Create the test database (synchronously)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop old tables
        await conn.run_sync(Base.metadata.create_all)  # Create new tables

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop the database after tests


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(db: AsyncSession):
    """
    Cleans the database before each test.
    """
    tables = ["users", "receipts", "receipt_items"]
    for table in tables:
        await db.execute(text(f"TRUNCATE {table} RESTART IDENTITY CASCADE;"))
    await db.commit()


@pytest_asyncio.fixture
async def db():
    """
    Provides an isolated database session for tests.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    """
    Creates a FastAPI test client with a test database.
    """

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
