from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime, date, timezone
from decimal import Decimal

class VendorMaster(Document):
    VendorID: int
    VendorCode: str
    VendorName: str
    Email: Optional[EmailStr] = None
    GSTID: Optional[str] = None
    CompanyPan: Optional[str] = None
    TAN: Optional[str] = None
    BankAccNo: Optional[str] = None
    BeneficiaryName: Optional[str] = None
    AccVerified: bool = False
    IfscCode: Optional[str] = None
    PaymentTermDays: Optional[int] = None
    UserPhone: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Settings:
        name = "vendor_master"


class VendorTransactions(Document):
    TransactionID: int
    VendorID: int
    InvoiceID: str
    ClientEntityID: int
    TransactionDate: date
    TransactionType: str
    Amount: Decimal
    Currency: str = "INR"
    Description: Optional[str] = None
    Notes: Optional[str] = None
    Status: int
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "vendor_transactions"
        
    class Config:
        json_encoders = {Decimal: float}


class ActionLog(Document):
    LogId: int
    Status: int
    Action: dict
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "action_log"


class TransactionLog(Document):
    LogID: int
    TransactionID: int
    Action: dict
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[int] = None
    UserLogID: Optional[int] = None
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Settings:
        name = "transaction_log"