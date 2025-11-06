
---

## ⚙️ Running the Project

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/fastapi-postgres-redis.git
cd fastapi-postgres-redis
docker-compose down   # stop old containers
docker-compose build --no-cache
docker-compose up -d

## 🚀 Features

- **User management**
  - Register new users
  - Seed test users (`user1..userN`)
  - Fetch user by username or ID

- **Daily check‑in system**
  - Tracks streaks, frozen days, and XP
  - Fair handling of missed days
  - Updates max streak automatically

- **Leaderboard**
  - Global leaderboard stored in Redis sorted set
  - Query top N users
  - Query league‑based slices (e.g. users 51–100)

- **Event‑driven architecture**
  - Producers publish `user_created` and `checkin` events to Redis Streams
  - Consumer listens and updates leaderboard in real time
  - Decoupled design: API doesn’t write directly to leaderboard
