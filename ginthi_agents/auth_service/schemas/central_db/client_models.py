from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from auth_service.db.database import Base

class Clients(Base):
    __tablename__ = "clients"
    
    ClientID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    Industry = Column(String(100))
    Website = Column(String(255))
    Email = Column(String(255))
    Phone = Column(String(50))
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    UpdatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lead_admins = relationship("LeadAdmins", back_populates="client")
    api_keys = relationship("ClientAPIKeys", back_populates="client")
    workflow_executions = relationship("WorkflowExecutions", back_populates="client")
    credit_entries = relationship("AICreditEntries", back_populates="client")
    credit_ledger = relationship("AICreditLedger", back_populates="client", uselist=False)
    feedbacks = relationship("Feedback", back_populates="client")


class LeadAdmins(Base):
    __tablename__ = "lead_admins"
    
    LeadAdminID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), nullable=False)
    Name = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    Phone = Column(String(50))
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    UpdatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Clients", back_populates="lead_admins")
    workflow_executions = relationship("WorkflowExecutions", back_populates="lead_admin")


class ClientAPIKeys(Base):
    __tablename__ = "client_api_keys"
    
    APIKeyID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), nullable=False)
    ApiKey = Column(String(512), nullable=False, unique=True)
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    ExpiresAt = Column(TIMESTAMP)
    IsActive = Column(Boolean, default=True)
    AccessControls = Column(Text)
    
    # Relationships
    client = relationship("Clients", back_populates="api_keys")
    workflow_executions = relationship("WorkflowExecutions", back_populates="api_key")