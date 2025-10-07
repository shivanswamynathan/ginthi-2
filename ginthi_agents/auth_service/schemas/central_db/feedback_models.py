from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from auth_service.db.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    FeedbackID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ExecutionID = Column(Integer, ForeignKey("workflow_executions.ExecutionID"), nullable=False)
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), nullable=False)
    Rating = Column(Integer, nullable=False) 
    Comments = Column(Text)
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    execution = relationship("WorkflowExecutions", back_populates="feedback")
    client = relationship("Clients", back_populates="feedbacks")