from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis


from app.schemas import UserCreate, UserRead
from app.database import get_db
from app.service import UserService


REDIS_URL = "redis://redis-server:6379"
router = APIRouter(prefix="/users", tags=["users"])
service = UserService()


@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await service.register_user(db, user.username, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed/{count}")
async def seed_users(count: int, db: AsyncSession = Depends(get_db)):
    """Create a batch of test users: user1..userN"""
    try:
        return await service.seed_users(db, count)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{username}", response_model=UserRead)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/checkin", response_model=UserRead)
async def checkin_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await service.checkin(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/leaderboard/top/{n}")
async def get_top_users(n: int):
    r = redis.from_url(REDIS_URL, decode_responses=True)
    top = await r.zrevrange("leaderboard:global", 0, n-1, withscores=True)
    await r.close()
    return [{"user_id": uid, "xp": xp} for uid, xp in top]
