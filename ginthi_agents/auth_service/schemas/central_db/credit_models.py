from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from auth_service.db.database import Base

class AICreditLedger(Base):
    __tablename__ = "ai_credit_ledger"
    
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), primary_key=True)
    CurrentBalance = Column(Integer, nullable=False, default=0)
    LastUpdated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Clients", back_populates="credit_ledger")


class AICreditEntries(Base):
    __tablename__ = "ai_credit_entries"
    
    CreditEntryID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), nullable=False)
    ExecutionID = Column(Integer, ForeignKey("workflow_executions.ExecutionID"), nullable=True)
    ChangeAmount = Column(Integer, nullable=False)  # Positive for credits added, negative for credits used
    Reason = Column(String(255))
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    client = relationship("Clients", back_populates="credit_entries")
    execution = relationship("WorkflowExecutions", back_populates="credit_entries")