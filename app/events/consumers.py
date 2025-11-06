import asyncio
import json
import redis.asyncio as redis

REDIS_URL = "redis://redis-server:6379"
LEADERBOARD_STREAM = "leaderboard_events"
LEADERBOARD_KEY = "leaderboard:global"

async def consume_leaderboard_events():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    last_id = "0-0"

    while True:
        # block until new events arrive
        events = await r.xread({LEADERBOARD_STREAM: last_id}, block=5000, count=10)
        if not events:
            continue

        for stream, messages in events:
            for msg_id, data in messages:
                event_type = data.get("event")
                user_id = data.get("user_id")
                xp = int(data.get("xp"))

                if event_type in ("user_created", "checkin"):
                    # update leaderboard sorted set
                    await r.zadd(LEADERBOARD_KEY, {f"user:{user_id}": xp})

                # advance the cursor
                last_id = msg_id

if __name__ == "__main__":
    asyncio.run(consume_leaderboard_events())
