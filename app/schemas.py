from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    xp: int
    streak: int
    max_streak: int
    frozen_days: int
    last_checkin: date | None
    last_streak_reset: date | None

    class Config:
        orm_mode = True
