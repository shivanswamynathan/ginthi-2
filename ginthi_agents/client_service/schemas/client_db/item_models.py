from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from client_service.db.postgres_db import Base


class ItemMaster(Base):
    __tablename__ = "item_master"

    item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    item_code = Column(String(50), nullable=False, unique=True)
    item_name = Column(String(255), nullable=False)
    hsn_code = Column(String(8), nullable=True)
    description = Column(Text, nullable=True)
    unit_measurement = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))