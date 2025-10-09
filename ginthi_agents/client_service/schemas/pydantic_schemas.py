from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from uuid import UUID


# ==================== CENTRAL CLIENT SCHEMAS ====================

class CentralClientBase(BaseModel):
    Name: str


class CentralClientCreate(CentralClientBase):
    pass


class CentralClientUpdate(CentralClientBase):
    pass


class CentralClientResponse(CentralClientBase):
    ClientID: UUID

    class Config:
        from_attributes = True


# ==================== CLIENT SCHEMAS ====================

class ClientBase(BaseModel):
    ClientName: str
    CentralClientID: Optional[UUID] = None
    CentralAPIKey: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    ClientID: UUID
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== CLIENT ENTITY SCHEMAS ====================

class ClientEntityBase(BaseModel):
    ClientID: UUID
    EntityName: str
    GSTID: Optional[str] = None
    CompanyPan: Optional[str] = None
    TAN: Optional[str] = None
    ParentClientID: Optional[UUID] = None


class ClientEntityCreate(ClientEntityBase):
    pass


class ClientEntityUpdate(ClientEntityBase):
    pass


class ClientEntityResponse(ClientEntityBase):
    EntityID: UUID

    class Config:
        from_attributes = True


# ==================== ROLE SCHEMAS ====================

class RoleBase(BaseModel):
    RoleName: str
    Description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleResponse(RoleBase):
    RoleID: UUID

    class Config:
        from_attributes = True


# ==================== PERMISSION SCHEMAS ====================

class PermissionBase(BaseModel):
    PermissionName: str
    Description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    PermissionID: UUID

    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    UserName: str
    Email: EmailStr
    UserPhone: Optional[str] = None


class UserCreate(UserBase):
    ClientID: UUID
    PasswordHash: str


class UserUpdate(UserBase):
    PasswordHash: Optional[str] = None


class UserResponse(UserBase):
    UserID: UUID
    ClientID: UUID
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== USER ROLE SCHEMAS ====================

class UserRoleCreate(BaseModel):
    UserID: UUID
    RoleID: UUID


class UserRoleResponse(BaseModel):
    UserID: UUID
    RoleID: UUID
    AssignedAt: datetime

    class Config:
        from_attributes = True


# ==================== ROLE PERMISSION SCHEMAS ====================

class RolePermissionCreate(BaseModel):
    RoleID: UUID
    PermissionID: UUID


class RolePermissionResponse(BaseModel):
    RoleID: UUID
    PermissionID: UUID

    class Config:
        from_attributes = True


# ==================== USER LOG SCHEMAS ====================

class UserLogCreate(BaseModel):
    UserID: UUID
    Action: dict


class UserLogUpdate(BaseModel):
    Action: dict


class UserLogResponse(BaseModel):
    LogId: UUID
    UserID: UUID
    Action: dict
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
    pass


class VendorUpdate(VendorBase):
    pass


class VendorResponse(VendorBase):
    VendorID: UUID
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION SCHEMAS ====================

class TransactionBase(BaseModel):
    VendorID: UUID
    InvoiceID: str
    ClientEntityID: UUID
    TransactionDate: date
    TransactionType: str
    Amount: Decimal
    Currency: str = "INR"
    Description: Optional[str] = None
    Notes: Optional[str] = None
    Status: int


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    TransactionID: UUID
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


# ==================== ACTION LOG SCHEMAS ====================

class ActionLogCreate(BaseModel):
    Status: int
    Action: dict


class ActionLogUpdate(BaseModel):
    Status: int
    Action: dict


class ActionLogResponse(BaseModel):
    LogId: UUID
    Status: int
    Action: dict
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION LOG SCHEMAS ====================

class TransactionLogCreate(BaseModel):
    TransactionID: UUID
    Action: dict
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[UUID] = None
    UserLogID: Optional[UUID] = None


class TransactionLogUpdate(BaseModel):
    Action: dict
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[UUID] = None
    UserLogID: Optional[UUID] = None


class TransactionLogResponse(BaseModel):
    LogID: UUID
    TransactionID: UUID
    Action: dict
    ApprovalTime: Optional[datetime] = None
    ActionLogID: Optional[UUID] = None
    UserLogID: Optional[UUID] = None
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
    pass


class ItemUpdate(ItemBase):
    pass


class ItemResponse(ItemBase):
    ItemID: UUID
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True


# ==================== WORKFLOW SCHEMAS ====================

class WorkflowBase(BaseModel):
    ClientID: UUID
    UserID: UUID
    WorkflowName: str
    RequestCount: int = 0
    LastRequestAt: Optional[datetime] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    LedgerID: UUID
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True