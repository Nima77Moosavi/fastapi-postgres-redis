from fastapi import APIRouter, Query, Depends, HTTPException
import redis.asyncio as redis

from app.schemas import UserCreate, UserRead
from app.service import UserService
from app.dependencies import get_user_service

REDIS_URL = "redis://redis-server:6379"
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserRead:
    try:
        return await user_service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed")
async def seed_users(
    count: int = Query(50, description="Number of users to seed"),
    user_service: UserService = Depends(get_user_service)
) -> list[UserRead]:
    """Create a batch of test users: user1..userN"""
    try:
        return await user_service.seed_users(count)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{username}")
async def get_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
) -> UserRead:
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{username}/checkin")
async def checkin_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
) -> UserRead:
    try:
        return await user_service.checkin(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/leaderboard")
@router.get("/leaderboard/league/{league}")
async def get_league_users(league: int = 1):
    r = redis.from_url(REDIS_URL, decode_responses=True)
    start = (league - 1) * 50
    end = start + 49
    users = await r.zrevrange("leaderboard:global", start, end, withscores=True)
    await r.close()
    return [{"user_id": user_id, "xp": xp} for user_id, xp in users]


@router.get("/leaderboard/top/{n}")
async def get_top_users(n: int):
    r = redis.from_url(REDIS_URL, decode_responses=True)
    users = await r.zrevrange("leaderboard:global", 0, n - 1, withscores=True)
    await r.close()
    return [{"user_id": uid, "xp": xp} for uid, xp in users]
