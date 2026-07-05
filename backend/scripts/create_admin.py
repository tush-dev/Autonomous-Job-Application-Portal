"""Create an admin user."""
import asyncio
import uuid
from getpass import getpass

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.user import User, UserSettings, UserRole


async def create_admin():
    print("Create Admin User")
    print("-" * 20)
    email = input("Email: ").strip()
    password = getpass("Password (min 12 chars): ").strip()
    name = input("Full name: ").strip()

    if len(password) < 12:
        print("Error: Password must be at least 12 characters")
        return

    async with async_session_factory() as session:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=get_password_hash(password),
            full_name=name,
            role=UserRole.ADMIN,
            is_verified=True,
        )
        session.add(user)
        session.add(UserSettings(user_id=user.id))
        await session.commit()
        print(f"✓ Admin user '{email}' created successfully!")


if __name__ == "__main__":
    asyncio.run(create_admin())
