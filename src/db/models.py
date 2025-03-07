from sqlalchemy import (
    Integer, BigInteger, String, Text, DateTime, ForeignKey, Float,
    Boolean, JSON, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(40))

