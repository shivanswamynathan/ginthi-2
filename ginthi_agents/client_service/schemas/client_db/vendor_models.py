from beanie import Document, Link
from pydantic import Field, EmailStr
from typing import Optional, TYPE_CHECKING
from datetime import datetime, date, timezone
from decimal import Decimal

if TYPE_CHECKING:
    from client_service.schemas.client_db.client_models import ClientEntity

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

    vendor: Optional[Link[VendorMaster]] = None
    client_entity: Optional[Link["ClientEntity"]] = None

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
    
    transaction: Optional[Link[VendorTransactions]] = None
    action_log: Optional[Link[ActionLog]] = None


    class Settings:
        name = "transaction_log"