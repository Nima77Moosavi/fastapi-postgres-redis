from fastapi import APIRouter, Depends, HTTPException
import redis.asyncio as redis

from app.schemas import UserCreate, UserRead
from app.service import UserService
from app.dependencies import get_user_service

REDIS_URL = "redis://redis-server:6379"
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.register_user(user.username, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed/{count}", response_model=list[UserRead])
async def seed_users(
    count: int,
    user_service: UserService = Depends(get_user_service)
):
    """Create a batch of test users: user1..userN"""
    try:
        return await user_service.seed_users(count)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{username}", response_model=UserRead)
async def get_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/checkin", response_model=UserRead)
async def checkin_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.checkin(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/leaderboard/top/{n}")
async def get_top_users(n: int):
    r = redis.from_url(REDIS_URL, decode_responses=True)
    top = await r.zrevrange("leaderboard:global", 0, n - 1, withscores=True)
    await r.close()
    return [{"user_id": uid, "xp": xp} for uid, xp in top]
