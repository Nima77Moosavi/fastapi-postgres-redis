import json
from datetime import datetime
import redis.asyncio as redis  # modern redis client with asyncio support

REDIS_URL = "redis://redis-server:6379"


async def publish_checkin_event(user_id: int, xp: int, streak: int):
    r = redis.from_url(REDIS_URL, decode_responses=True)
    event = {
        "event": "checkin",
        "user_id": user_id,
        "xp": xp,
        "streak": streak,
        "timestamp": datetime.utcnow().isoformat()
    }
    await r.xadd("checkin_streams", event)
    await r.close()
