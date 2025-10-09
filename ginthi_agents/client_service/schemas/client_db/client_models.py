from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from client_service.db.postgres_db import Base


class CentralClients(Base):
    __tablename__ = "central_clients"

    ClientID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    Name = Column(String(255), nullable=False)

    # Relationships
    clients = relationship("Clients", back_populates="central_client")


class Clients(Base):
    __tablename__ = "clients"

    ClientID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ClientName = Column(String(255), nullable=False, unique=True)
    CentralClientID = Column(UUID(as_uuid=True), ForeignKey("central_clients.ClientID"), nullable=True)
    CentralAPIKey = Column(String(512), nullable=True)
    CreatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    central_client = relationship("CentralClients", back_populates="clients")
    entities = relationship("ClientEntity", back_populates="client", cascade="all, delete-orphan")
    users = relationship("Users", back_populates="client", cascade="all, delete-orphan")
    workflows = relationship("WorkflowRequestLedger", back_populates="client", cascade="all, delete-orphan")


class ClientEntity(Base):
    __tablename__ = "client_entity"

    EntityID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ClientID = Column(UUID(as_uuid=True), ForeignKey("clients.ClientID"), nullable=False, index=True)
    GSTID = Column(String(13), nullable=True)
    CompanyPan = Column(String(13), nullable=True)
    EntityName = Column(String(100), nullable=False)
    TAN = Column(String(13), nullable=True)
    ParentClientID = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    client = relationship("Clients", back_populates="entities")
    transactions = relationship("VendorTransactions", back_populates="client_entity", cascade="all, delete-orphan")