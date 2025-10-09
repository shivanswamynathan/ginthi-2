from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from client_service.db.postgres_db import Base


class WorkflowRequestLedger(Base):
    __tablename__ = "workflow_request_ledger"

    LedgerID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ClientID = Column(UUID(as_uuid=True), ForeignKey("clients.ClientID"), nullable=False, index=True)
    UserID = Column(UUID(as_uuid=True), ForeignKey("users.UserID"), nullable=False, index=True)
    WorkflowName = Column(String(255), nullable=False)
    RequestCount = Column(Integer, default=0)
    LastRequestAt = Column(DateTime(timezone=True), nullable=True)
    CreatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    client = relationship("Clients", back_populates="workflows")
    user = relationship("Users", back_populates="workflows")