from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from client_service.db.postgres_db import Base


class VendorMaster(Base):
    __tablename__ = "vendor_master"

    VendorID = Column(Integer, primary_key=True, index=True)
    VendorCode = Column(String(50), nullable=False, unique=True)
    VendorName = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=True)
    GSTID = Column(String(13), nullable=True)
    CompanyPan = Column(String(13), nullable=True)
    TAN = Column(String(13), nullable=True)
    BankAccNo = Column(String(13), nullable=True)
    BeneficiaryName = Column(String(255), nullable=True)
    AccVerified = Column(Boolean, default=False)
    IfscCode = Column(String(13), nullable=True)
    PaymentTermDays = Column(Integer, nullable=True)
    UserPhone = Column(String(13), nullable=True)
    CreatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    transactions = relationship("VendorTransactions", back_populates="vendor", cascade="all, delete-orphan")


class VendorTransactions(Base):
    __tablename__ = "vendor_transactions"

    TransactionID = Column(Integer, primary_key=True, index=True)
    VendorID = Column(Integer, ForeignKey("vendor_master.VendorID"), nullable=False, index=True)
    InvoiceID = Column(String(50), nullable=False, unique=True)
    ClientEntityID = Column(Integer, ForeignKey("client_entity.EntityID"), nullable=False, index=True)
    TransactionDate = Column(Date, nullable=False)
    TransactionType = Column(String(50), nullable=False)
    Amount = Column(Numeric(18, 4), nullable=False)
    Currency = Column(String(10), default="INR")
    Description = Column(Text, nullable=True)
    Notes = Column(Text, nullable=True)
    Status = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    vendor = relationship("VendorMaster", back_populates="transactions")
    client_entity = relationship("ClientEntity", back_populates="transactions")
    transaction_logs = relationship("TransactionLog", back_populates="transaction", cascade="all, delete-orphan")


class ActionLog(Base):
    __tablename__ = "action_log"

    LogId = Column(Integer, primary_key=True, index=True)
    Status = Column(Integer, nullable=False)
    Action = Column(JSONB, nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction_logs = relationship("TransactionLog", back_populates="action_log")


class TransactionLog(Base):
    __tablename__ = "transaction_log"

    LogID = Column(Integer, primary_key=True, index=True)
    TransactionID = Column(Integer, ForeignKey("vendor_transactions.TransactionID"), nullable=False, index=True)
    Action = Column(JSONB, nullable=False)
    ApprovalTime = Column(DateTime(timezone=True), nullable=True)
    ActionLogID = Column(Integer, ForeignKey("action_log.LogId"), nullable=True, index=True)
    UserLogID = Column(Integer, nullable=True)
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("VendorTransactions", back_populates="transaction_logs")
    action_log = relationship("ActionLog", back_populates="transaction_logs")