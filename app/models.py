from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255), unique=True, index=True)
    retry_count = Column(Integer, default=3)
    cooldown = Column(Integer, default=10)  # in seconds
    last_status = Column(Boolean, default=None)
    last_response_time = Column(Float, default=None)
    last_checked = Column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now()
    )

    history = relationship("PingHistory", back_populates="target", cascade="all, delete")


class PingHistory(Base):
    __tablename__ = "ping_history"

    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey("targets.id", ondelete="CASCADE"))
    status = Column(Boolean)
    response_time = Column(Float)
    checked_at = Column(DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"))

    target = relationship("Target", back_populates="history")
