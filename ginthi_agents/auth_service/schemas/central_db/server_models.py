from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from auth_service.db.database import Base

class ClientServers(Base):
    __tablename__ = "client_servers"
    
    ServerID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ClientID = Column(Integer, ForeignKey("clients.ClientID"), nullable=False)
    ServerName = Column(String(255), nullable=False)
    ServerURL = Column(String(255))
    ServerIP = Column(String(50))
    ServerPort = Column(Integer)
    ServerType = Column(String(50))  # 'Production', 'Staging', 'Development'
    Username = Column(String(255))
    Password = Column(String(512))  # Store encrypted!
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    UpdatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Clients", back_populates="servers")