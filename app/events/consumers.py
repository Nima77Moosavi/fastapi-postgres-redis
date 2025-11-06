import asyncio
import redis.asyncio as redis
from datetime import datetime

REDIS_URL = "redis://redis-server:6379"
LEADERBOARD_STREAM = "leaderboard_events"
LEADERBOARD_KEY = "leaderboard:global"

async def consume_leaderboard_events():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    last_id = "0-0"

    # Startup log
    print(f"[{datetime.utcnow().isoformat()}] Consumer started, connecting to {REDIS_URL}, listening on stream '{LEADERBOARD_STREAM}'")

    while True:
        try:
            events = await r.xread({LEADERBOARD_STREAM: last_id}, block=5000, count=10)
            if not events:
                continue

            for stream, messages in events:
                for msg_id, data in messages:
                    event_type = data.get("event")
                    user_id = data.get("user_id")
                    xp = int(data.get("xp"))

                    # Event receipt log
                    print(f"[{datetime.utcnow().isoformat()}] Received event={event_type}, user_id={user_id}, xp={xp}, raw={data}")

                    if event_type in ("user_created", "checkin"):
                        try:
                            await r.zadd(LEADERBOARD_KEY, {str(user_id): xp})
                            # Leaderboard update log
                            print(f"[{datetime.utcnow().isoformat()}] Leaderboard updated: user {user_id} -> {xp}")
                        except Exception as e:
                            # Error log
                            print(f"[{datetime.utcnow().isoformat()}] ERROR updating leaderboard for user {user_id}: {e}")

                    # Advance the cursor
                    last_id = msg_id

        except Exception as e:
            print(f"[{datetime.utcnow().isoformat()}] ERROR in consumer loop: {e}")
            await asyncio.sleep(1)  # prevent tight crash loop

if __name__ == "__main__":
    asyncio.run(consume_leaderboard_events())
