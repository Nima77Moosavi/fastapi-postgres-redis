from datetime import date, timedelta

from app.repository import UserRepository
from app.events.producers import publish_checkin_event
from app.schemas import UserCreate

import redis.asyncio as redis

import random

REDIS_URL = "redis://redis-server:6379"
LEADERBOARD_KEY = "leaderboard:global"


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def seed_users(self, count: int):
        """Register the entered amount of test users"""
        users = []
        r = redis.from_url(REDIS_URL, decode_responses=True)
        for i in range(1, count + 1):
            username = f"user{i}"
            password = f"pass{i}"
            xp = random.randint(1, 100) * 10
            existing = await self.repo.get_by_username(username)
            if existing:
                # skip or update instead of failing
                continue
            user = await self.repo.create_user(username, password, xp)
            users.append(user)

            await r.zadd(LEADERBOARD_KEY, {f"user:{user.id}": user.xp})
        await r.close()
        return users

    async def register_user(self, user: UserCreate):
        """Register a new user if username is unique."""
        existing = await self.repo.get_by_username(user.username)
        if existing:
            raise ValueError("Username already exists")
        return await self.repo.create_user(
            username=user.username,
            password=user.password,
            xp=user.xp,
            frozen_days=user.frozen_days,
            streak=user.streak,
        )

    async def get_user_by_username(self, username: str):
        """Fetch a user by username."""
        return await self.repo.get_by_username(username)

    async def get_user_by_id(self, user_id: int):
        """Fetch a user by ID."""
        return await self.repo.get_by_id(user_id)

    async def update_user(self, user):
        """Persist changes to a user."""
        return await self.repo.update_user(user)

    async def checkin(self, user_id: int):
        """Daily check‑in logic: update streaks, XP, frozen days."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        today = date.today()

        # Already checked in today
        if user.last_checkin == today:
            return user

        # Consecutive day
        if user.last_checkin == today - timedelta(days=1):
            user.streak += 1
        else:
            # Missed a day
            if user.frozen_days > 0:
                user.frozen_days -= 1
            else:
                user.streak = 1  # reset streak

        # Update max streak
        if user.streak > user.max_streak:
            user.max_streak = user.streak

        # Add XP
        user.xp += 10  # reward per check‑in

        # Update last_checkin
        user.last_checkin = today

        user = await self.repo.update_user(user)

        await publish_checkin_event(user.id, user.xp, user.streak)

        return user
