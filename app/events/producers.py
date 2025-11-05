import json
import aioredis
from datetime import datetime


REDIS_URL = "redis://redis-server:6379"


async def publish_checkin_event(user_id: int, xp: int, streak: int):
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    event = {
        "event": "checkin",
        "user_id": user_id,
        "xp": xp,
        "streak": streak,
        "timestamp": datetime.utcnow().isoformat()
    }
    await redis.xadd("checkin_streams", event)
    await redis.close()
