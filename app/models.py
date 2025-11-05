from datetime import date
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base   # <-- import the single Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))

    xp: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    frozen_days: Mapped[int] = mapped_column(Integer, default=0)

    last_checkin: Mapped[date | None] = mapped_column()
    last_streak_reset: Mapped[date | None] = mapped_column()

    def __repr__(self) -> str:
        return f"<User(username={self.username}, xp={self.xp}, streak={self.streak})>"
