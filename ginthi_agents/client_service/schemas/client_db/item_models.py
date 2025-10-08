from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from client_service.db.postgres_db import Base


class ItemMaster(Base):
    __tablename__ = "item_master"

    ItemID = Column(Integer, primary_key=True, index=True)
    ItemCode = Column(String(50), nullable=False, unique=True)
    ItemName = Column(String(255), nullable=False)
    HSNCode = Column(String(13), nullable=True)
    Description = Column(Text, nullable=True)
    UnitMeasurement = Column(String(12), nullable=True)
    CreatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))