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

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[str] = mapped_column(String(30), index=True)
    principal: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    service: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    indicator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_event: Mapped[dict] = mapped_column(JSON)
    occurred_at: Mapped[object] = mapped_column(DateTime(timezone=True), index=True)
    correlated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())

