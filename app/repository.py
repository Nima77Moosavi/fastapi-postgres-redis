from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User


class UserRepository:
    async def create_user(self, db: AsyncSession, username: str, password: str) -> User:
        """Create and persist a new user."""
        user = User(username=username, password=password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Fetch a user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        """Fetch a user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def update_user(self, db: AsyncSession, user: User) -> User:
        """Update an existing user and persist changes."""
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
