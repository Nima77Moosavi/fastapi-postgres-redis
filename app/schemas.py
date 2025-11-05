from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class UserCreate(BaseModel):
    username: str
    password: str
    xp: int = Field(default=0, description="initial xp, default = 0")
    frozen_days: int = Field(
        default=0, description="initial frozen_days, default = 0")
    streak: int = Field(default=0, description="initial streak, default = 0")


class UserRead(BaseModel):
    id: int
    username: str
    xp: int
    streak: int
    max_streak: int
    frozen_days: int
    last_checkin: date | None
    last_streak_reset: date | None

    model_config = ConfigDict(from_attributes=True)
