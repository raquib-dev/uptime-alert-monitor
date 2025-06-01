from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String, unique=True, index=True)
    retry_count = Column(Integer, default=3)
    cooldown = Column(Integer, default=10)  # seconds
    last_status = Column(Boolean, default=None)
    last_response_time = Column(Float, default=None)
    last_checked = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PingHistory(Base):
    __tablename__ = "ping_history"

    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    status = Column(Boolean)
    response_time = Column(Float)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    target = relationship("Target", backref="history")