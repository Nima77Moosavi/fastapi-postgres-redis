from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User

import redis.asyncio as redis


REDIS_URL = "redis://redis-server:6379"
LEADERBOARD_KEY = "leaderboard:global"


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, username: str, password: str, xp: int) -> User:
        """Create and persist a new user ."""
        user = User(username=username, password=password, xp=xp)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_username(self, username: str) -> User | None:
        """Fetch a user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def update_user(self, user: User) -> User:
        """Update an existing user and persist changes."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
