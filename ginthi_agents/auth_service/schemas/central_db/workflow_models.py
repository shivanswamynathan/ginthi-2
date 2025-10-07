from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from auth_service.db.database import Base

class Workflows(Base):
    __tablename__ = "workflows"
    
    WorkflowID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    Description = Column(Text)
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    UpdatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workflow_executions = relationship("WorkflowExecutions", back_populates="workflow")


class WorkflowExecutions(Base):
    __tablename__ = "workflow_executions"
    
    ExecutionID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), nullable=False)
    WorkflowID = Column(Integer, ForeignKey("workflows.WorkflowID"), nullable=False)
    LeadAdminID = Column(Integer, ForeignKey("lead_admins.LeadAdminID"), nullable=True)
    APIKeyID = Column(Integer, ForeignKey("client_api_keys.APIKeyID"), nullable=True)
    ExecutionTimestamp = Column(TIMESTAMP, server_default=func.now())
    Status = Column(String(50))
    DurationSeconds = Column(Integer)
    
    # Relationships
    client = relationship("Clients", back_populates="workflow_executions")
    workflow = relationship("Workflows", back_populates="workflow_executions")
    lead_admin = relationship("LeadAdmins", back_populates="workflow_executions")
    api_key = relationship("ClientAPIKeys", back_populates="workflow_executions")
    credit_entries = relationship("AICreditEntries", back_populates="execution")
    feedback = relationship("Feedback", back_populates="execution", uselist=False)