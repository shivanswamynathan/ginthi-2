from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class VendorMaster(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
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
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VendorTransactions(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
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
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, Decimal: float}

class TransactionLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    LogID: int
    TransactionID: int
    Action: dict  # JSONB
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[int] = None
    UserLogID: Optional[int] = None
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ActionLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    LogId: int
    Status: int
    Action: dict  # JSONB
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}