from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


# ==================== CENTRAL CLIENT SCHEMAS ====================

class CentralClientBase(BaseModel):
    Name: str


class CentralClientCreate(CentralClientBase):
    ClientID: int


class CentralClientUpdate(CentralClientBase):
    pass


class CentralClientResponse(CentralClientBase):
    ClientID: int

    class Config:
        from_attributes = True


# ==================== CLIENT SCHEMAS ====================

class ClientBase(BaseModel):
    ClientName: str
    CentralClientID: Optional[int] = None
    CentralAPIKey: Optional[str] = None


class ClientCreate(ClientBase):
    ClientID: int


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    ClientID: int
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== CLIENT ENTITY SCHEMAS ====================

class ClientEntityBase(BaseModel):
    ClientID: int
    EntityName: str
    GSTID: Optional[str] = None
    CompanyPan: Optional[str] = None
    TAN: Optional[str] = None
    ParentClientID: Optional[int] = None


class ClientEntityCreate(ClientEntityBase):
    EntityID: int


class ClientEntityUpdate(ClientEntityBase):
    pass


class ClientEntityResponse(ClientEntityBase):
    EntityID: int

    class Config:
        from_attributes = True


# ==================== ROLE SCHEMAS ====================

class RoleBase(BaseModel):
    RoleName: str
    Description: Optional[str] = None


class RoleCreate(RoleBase):
    RoleID: int


class RoleUpdate(RoleBase):
    pass


class RoleResponse(RoleBase):
    RoleID: int

    class Config:
        from_attributes = True


# ==================== PERMISSION SCHEMAS ====================

class PermissionBase(BaseModel):
    PermissionName: str
    Description: Optional[str] = None


class PermissionCreate(PermissionBase):
    PermissionID: int


class PermissionUpdate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    PermissionID: int

    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    UserName: str
    Email: EmailStr
    UserPhone: Optional[str] = None


class UserCreate(UserBase):
    UserID: int
    ClientID: int
    PasswordHash: str


class UserUpdate(UserBase):
    PasswordHash: Optional[str] = None


class UserResponse(UserBase):
    UserID: int
    ClientID: int
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== USER ROLE SCHEMAS ====================

class UserRoleCreate(BaseModel):
    UserID: int
    RoleID: int


class UserRoleResponse(BaseModel):
    UserID: int
    RoleID: int
    AssignedAt: datetime

    class Config:
        from_attributes = True


# ==================== ROLE PERMISSION SCHEMAS ====================

class RolePermissionCreate(BaseModel):
    RoleID: int
    PermissionID: int


class RolePermissionResponse(BaseModel):
    RoleID: int
    PermissionID: int

    class Config:
        from_attributes = True


# ==================== USER LOG SCHEMAS ====================

class UserLogCreate(BaseModel):
    LogId: int
    UserID: int
    Action: dict


class UserLogUpdate(BaseModel):
    Action: dict


class UserLogResponse(UserLogCreate):
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== VENDOR SCHEMAS ====================

class VendorBase(BaseModel):
    VendorName: str
    VendorCode: str
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


class VendorCreate(VendorBase):
    VendorID: int


class VendorUpdate(VendorBase):
    pass


class VendorResponse(VendorBase):
    VendorID: int
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION SCHEMAS ====================

class TransactionBase(BaseModel):
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


class TransactionCreate(TransactionBase):
    TransactionID: int


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    TransactionID: int
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


# ==================== ACTION LOG SCHEMAS ====================

class ActionLogCreate(BaseModel):
    LogId: int
    Status: int
    Action: dict


class ActionLogUpdate(BaseModel):
    Status: int
    Action: dict


class ActionLogResponse(ActionLogCreate):
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION LOG SCHEMAS ====================

class TransactionLogCreate(BaseModel):
    LogID: int
    TransactionID: int
    Action: dict
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[int] = None
    UserLogID: Optional[int] = None


class TransactionLogUpdate(BaseModel):
    Action: dict
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[int] = None
    UserLogID: Optional[int] = None


class TransactionLogResponse(TransactionLogCreate):
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== ITEM SCHEMAS ====================

class ItemBase(BaseModel):
    ItemCode: str
    ItemName: str
    HSNCode: Optional[str] = None
    Description: Optional[str] = None
    UnitMeasurement: Optional[str] = None


class ItemCreate(ItemBase):
    ItemID: int


class ItemUpdate(ItemBase):
    pass


class ItemResponse(ItemBase):
    ItemID: int
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== WORKFLOW SCHEMAS ====================

class WorkflowBase(BaseModel):
    ClientID: int
    UserID: int
    WorkflowName: str
    RequestCount: int = 0
    LastRequestAt: Optional[datetime] = None


class WorkflowCreate(WorkflowBase):
    LedgerID: int


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    LedgerID: int
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True