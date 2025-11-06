from fastapi import HTTPException

from app.repository import UserRepository
from app.events.producers import publish_leaderboard_event
from app.schemas import UserCreate

import redis.asyncio as redis

from datetime import date, timedelta
import random


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def seed_users(self, count: int):
        """Register the entered amount of test users"""
        users = []
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

            await publish_leaderboard_event("user_created", user.id, user.xp, user.streak)
        return users

    async def register_user(self, user: UserCreate):
        """Register a new user if username is unique."""
        existing = await self.repo.get_by_username(user.username)
        if existing:
            raise ValueError("Username already exists")
        user = await self.repo.create_user(user.username, user.password)

        await publish_leaderboard_event("user_created", user.id, user.xp, user.streak)

        return user

    async def get_user_by_username(self, username: str):
        """Fetch a user by username."""
        return await self.repo.get_by_username(username)

    async def get_user_by_id(self, user_id: int):
        """Fetch a user by ID."""
        return await self.repo.get_by_id(user_id)

    async def update_user(self, user):
        """Persist changes to a user."""
        return await self.repo.update_user(user)

    async def checkin(self, username: str):
        """Daily check‑in logic: update streaks, XP, frozen days."""
        user = await self.repo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        today = date.today()

        # Already checked in today
        if user.last_checkin == today:
            raise HTTPException(
                status_code=400, detail="Already checked in today")

        if not user.last_checkin:
            # First ever check‑in: start streak
            user.streak = 1
        else:
            delta = (today - user.last_checkin).days

            if delta == 1:
                # Consecutive day
                user.streak += 1
            elif delta > 1:
                # Missed days
                missed_days = delta - 1
                if user.frozen_days >= missed_days:
                    # Burn frozen days equal to missed days, continue streak
                    user.frozen_days -= missed_days
                    user.streak += 1
                else:
                    # Not enough frozen days → reset streak
                    user.streak = 1
                    user.frozen_days = 0
                    # Optionally: grant 1 frozen day here if that's your rule
                    # user.frozen_days = 1

        # Update max streak
        if user.streak > user.max_streak:
            user.max_streak = user.streak

        # Add XP
        user.xp += 10

        # Update last_checkin
        user.last_checkin = today

        user = await self.repo.update_user(user)

        await publish_leaderboard_event("checkin", user.id, user.xp, user.streak)

        return user
