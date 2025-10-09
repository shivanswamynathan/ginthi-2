from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from uuid import UUID


# ==================== CENTRAL CLIENT SCHEMAS ====================

class CentralClientBase(BaseModel):
    name: str


class CentralClientCreate(CentralClientBase):
    pass


class CentralClientUpdate(CentralClientBase):
    pass


class CentralClientResponse(CentralClientBase):
    client_id: UUID

    class Config:
        from_attributes = True


# ==================== CLIENT SCHEMAS ====================

class ClientBase(BaseModel):
    client_name: str
    central_client_id: Optional[UUID] = None
    central_api_key: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    client_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== CLIENT ENTITY SCHEMAS ====================

class ClientEntityBase(BaseModel):
    client_id: UUID
    entity_name: str
    gst_id: Optional[str] = None
    company_pan: Optional[str] = None
    tan: Optional[str] = None
    parent_client_id: Optional[UUID] = None


class ClientEntityCreate(ClientEntityBase):
    pass


class ClientEntityUpdate(ClientEntityBase):
    pass


class ClientEntityResponse(ClientEntityBase):
    entity_id: UUID

    class Config:
        from_attributes = True


# ==================== ROLE SCHEMAS ====================

class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleResponse(RoleBase):
    role_id: UUID

    class Config:
        from_attributes = True


# ==================== PERMISSION SCHEMAS ====================

class PermissionBase(BaseModel):
    permission_name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    permission_id: UUID

    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    user_name: str
    email: EmailStr
    user_phone: Optional[str] = None


class UserCreate(UserBase):
    client_id: UUID
    password_hash: str


class UserUpdate(UserBase):
    password_hash: Optional[str] = None


class UserResponse(UserBase):
    user_id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== USER ROLE SCHEMAS ====================

class UserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID


class UserRoleResponse(BaseModel):
    user_id: UUID
    role_id: UUID
    assigned_at: datetime

    class Config:
        from_attributes = True


# ==================== ROLE PERMISSION SCHEMAS ====================

class RolePermissionCreate(BaseModel):
    role_id: UUID
    permission_id: UUID


class RolePermissionResponse(BaseModel):
    role_id: UUID
    permission_id: UUID

    class Config:
        from_attributes = True


# ==================== USER LOG SCHEMAS ====================

class UserLogCreate(BaseModel):
    user_id: UUID
    action: dict


class UserLogUpdate(BaseModel):
    action: dict


class UserLogResponse(BaseModel):
    log_id: UUID
    user_id: UUID
    action: dict
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== VENDOR SCHEMAS ====================

class VendorBase(BaseModel):
    vendor_name: str
    vendor_code: str
    email: Optional[EmailStr] = None
    gst_id: Optional[str] = None
    company_pan: Optional[str] = None
    tan: Optional[str] = None
    bank_acc_no: Optional[str] = None
    beneficiary_name: Optional[str] = None
    acc_verified: bool = False
    ifsc_code: Optional[str] = None
    payment_term_days: Optional[int] = None
    user_phone: Optional[str] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(VendorBase):
    pass


class VendorResponse(VendorBase):
    vendor_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION SCHEMAS ====================

class TransactionBase(BaseModel):
    vendor_id: UUID
    invoice_id: str
    client_entity_id: UUID
    transaction_date: date
    transaction_type: str
    amount: Decimal
    currency: str = "INR"
    description: Optional[str] = None
    notes: Optional[str] = None
    status: int


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    transaction_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


# ==================== ACTION LOG SCHEMAS ====================

class ActionLogCreate(BaseModel):
    status: int
    action: dict


class ActionLogUpdate(BaseModel):
    status: int
    action: dict


class ActionLogResponse(BaseModel):
    log_id: UUID
    status: int
    action: dict
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION LOG SCHEMAS ====================

class TransactionLogCreate(BaseModel):
    transaction_id: UUID
    action: dict
    approval_time: Optional[datetime] = None
    action_log_id: Optional[UUID] = None
    user_log_id: Optional[UUID] = None


class TransactionLogUpdate(BaseModel):
    action: dict
    approval_time: Optional[datetime] = None
    action_log_id: Optional[UUID] = None
    user_log_id: Optional[UUID] = None


class TransactionLogResponse(BaseModel):
    log_id: UUID
    transaction_id: UUID
    action: dict
    approval_time: Optional[datetime] = None
    action_log_id: Optional[UUID] = None
    user_log_id: Optional[UUID] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== ITEM SCHEMAS ====================

class ItemBase(BaseModel):
    item_code: str
    item_name: str
    hsn_code: Optional[str] = None
    description: Optional[str] = None
    unit_measurement: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemResponse(ItemBase):
    item_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== WORKFLOW SCHEMAS ====================

class WorkflowBase(BaseModel):
    client_id: UUID
    user_id: UUID
    workflow_name: str
    request_count: int = 0
    last_request_at: Optional[datetime] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    ledger_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True