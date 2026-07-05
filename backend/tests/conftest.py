import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserSettings, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker(test_engine, expire_on_commit=False)() as session:
        yield session


@pytest.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_session) -> User:
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestP@ss1234"),
        full_name="Test User",
        role=UserRole.USER,
        is_verified=True,
    )
    test_session.add(user)
    test_session.add(UserSettings(user_id=user.id))
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(test_session) -> User:
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("AdminP@ss1234"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_verified=True,
    )
    test_session.add(user)
    test_session.add(UserSettings(user_id=user.id))
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(client, test_user) -> dict:
    from app.core.security import create_access_token
    token = create_access_token(subject=str(test_user.id), role=test_user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client, admin_user) -> dict:
    from app.core.security import create_access_token
    token = create_access_token(subject=str(admin_user.id), role=admin_user.role.value)
    return {"Authorization": f"Bearer {token}"}
