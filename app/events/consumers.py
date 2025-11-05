import asyncio
import redis.asyncio as redis  # ✅ use redis.asyncio

REDIS_URL = "redis://redis-server:6379"

async def consume_checkins():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    last_id = "0-0"

    while True:
        # block until new events arrive
        events = await r.xread({"checkin_streams": last_id}, block=5000, count=10)
        if not events:
            continue

        for stream, messages in events:
            for msg_id, data in messages:
                user_id = data["user_id"]
                xp = int(data["xp"])

                # update leaderboard sorted set
                await r.zadd("leaderboard:global", {user_id: xp})

                last_id = msg_id

if __name__ == "__main__":
    asyncio.run(consume_checkins())
