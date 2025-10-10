from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from uuid import UUID


# ==================== CENTRAL CLIENT SCHEMAS ====================

class CentralClientBase(BaseModel):
    """Base schema for central client information"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the central client organization",
        examples=["Acme Holdings Inc"]
    )


class CentralClientCreate(CentralClientBase):
    """Schema for creating a new central client"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Holdings Inc"
            }
        }


class CentralClientUpdate(CentralClientBase):
    """Schema for updating an existing central client"""
    pass


class CentralClientResponse(CentralClientBase):
    """Schema for central client response data"""
    client_id: UUID = Field(..., description="Unique identifier for the central client")

    class Config:
        from_attributes = True


# ==================== CLIENT SCHEMAS ====================

class ClientBase(BaseModel):
    """Base schema for client information"""
    client_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique name of the client organization",
        examples=["Acme Corporation"]
    )
    central_client_id: Optional[UUID] = Field(
        None,
        description="Optional UUID of the parent central client"
    )
    central_api_key: Optional[str] = Field(
        None,
        max_length=512,
        description="API key for central client authentication"
    )


class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    class Config:
        json_schema_extra = {
            "example": {
                "client_name": "Acme Corporation",
                "central_client_id": "123e4567-e89b-12d3-a456-426614174000",
                "central_api_key": "sk_test_1234567890abcdef"
            }
        }


class ClientUpdate(ClientBase):
    """Schema for updating an existing client"""
    pass


class ClientResponse(ClientBase):
    """Schema for client response data"""
    client_id: UUID = Field(..., description="Unique identifier for the client")
    created_at: datetime = Field(..., description="Timestamp when client was created")
    updated_at: datetime = Field(..., description="Timestamp when client was last updated")

    class Config:
        from_attributes = True


# ==================== CLIENT ENTITY SCHEMAS ====================

class ClientEntityBase(BaseModel):
    """Base schema for client entity information"""
    client_id: UUID = Field(
        ...,
        description="UUID of the parent client organization"
    )
    entity_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the client entity (branch/subsidiary)",
        examples=["Acme Corp - Mumbai Branch"]
    )
    gst_id: Optional[str] = Field(
        None,
        max_length=15,
        description="GST identification number for this entity",
        examples=["29ABCDE1234F1Z5"]
    )
    company_pan: Optional[str] = Field(
        None,
        max_length=10,
        description="PAN card number of the entity",
        examples=["ABCDE1234F"]
    )
    tan: Optional[str] = Field(
        None,
        max_length=10,
        description="Tax deduction account number",
        examples=["ABCD12345E"]
    )
    parent_client_id: Optional[UUID] = Field(
        None,
        description="Optional UUID of parent client entity for hierarchical structure"
    )


class ClientEntityCreate(ClientEntityBase):
    """Schema for creating a new client entity"""
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "entity_name": "Acme Corp - Mumbai Branch",
                "gst_id": "29ABCDE1234F1Z5",
                "company_pan": "ABCDE1234F",
                "tan": "ABCD12345E"
            }
        }


class ClientEntityUpdate(ClientEntityBase):
    """Schema for updating an existing client entity"""
    pass


class ClientEntityResponse(ClientEntityBase):
    """Schema for client entity response data"""
    entity_id: UUID = Field(..., description="Unique identifier for the entity")

    class Config:
        from_attributes = True


# ==================== ROLE SCHEMAS ====================

class RoleBase(BaseModel):
    """Base schema for role information"""
    role_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Name of the role",
        examples=["Admin", "Manager", "Accountant", "Viewer"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the role and its responsibilities"
    )


class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "Accountant",
                "description": "Can view and manage financial transactions"
            }
        }


class RoleUpdate(RoleBase):
    """Schema for updating an existing role"""
    pass


class RoleResponse(RoleBase):
    """Schema for role response data"""
    role_id: UUID = Field(..., description="Unique identifier for the role")

    class Config:
        from_attributes = True


# ==================== PERMISSION SCHEMAS ====================

class PermissionBase(BaseModel):
    """Base schema for permission information"""
    permission_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the permission",
        examples=["create_user", "delete_transaction", "view_reports", "approve_invoice"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of what this permission allows"
    )


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission"""
    class Config:
        json_schema_extra = {
            "example": {
                "permission_name": "approve_invoice",
                "description": "Allows user to approve vendor invoices"
            }
        }


class PermissionUpdate(PermissionBase):
    """Schema for updating an existing permission"""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response data"""
    permission_id: UUID = Field(..., description="Unique identifier for the permission")

    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Base schema for user information"""
    user_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the user",
        examples=["John Doe"]
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address for login and communication",
        examples=["john.doe@example.com"]
    )
    user_phone: Optional[str] = Field(
        None,
        max_length=15,
        description="Optional phone number with country code",
        examples=["+1234567890", "+919876543210"]
    )


class UserCreate(UserBase):
    """Schema for creating a new user account"""
    client_id: UUID = Field(
        ...,
        description="UUID of the client organization this user belongs to"
    )
    password_hash: str = Field(
        ...,
        min_length=8,
        description="Hashed password for authentication (should be pre-hashed on client side)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "John Doe",
                "email": "john.doe@example.com",
                "password_hash": "$2b$12$KIXqH9P1qF.yGZ0p7YxZ9O",
                "user_phone": "+919876543210"
            }
        }


class UserUpdate(UserBase):
    """Schema for updating an existing user"""
    password_hash: Optional[str] = Field(
        None,
        min_length=8,
        description="New hashed password (optional, only if changing password)"
    )


class UserResponse(UserBase):
    """Schema for user response data"""
    user_id: UUID = Field(..., description="Unique identifier for the user")
    client_id: UUID = Field(..., description="UUID of the client organization")
    created_at: datetime = Field(..., description="Timestamp when user was created")
    updated_at: datetime = Field(..., description="Timestamp when user was last updated")

    class Config:
        from_attributes = True


# ==================== USER ROLE SCHEMAS ====================

class UserRoleCreate(BaseModel):
    """Schema for assigning a role to a user"""
    user_id: UUID = Field(
        ...,
        description="UUID of the user to assign the role to"
    )
    role_id: UUID = Field(
        ...,
        description="UUID of the role to assign"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role_id": "987fcdeb-51a2-43d7-9876-543210fedcba"
            }
        }


class UserRoleResponse(BaseModel):
    """Schema for user role response data"""
    user_id: UUID = Field(..., description="UUID of the user")
    role_id: UUID = Field(..., description="UUID of the assigned role")
    assigned_at: datetime = Field(..., description="Timestamp when role was assigned")

    class Config:
        from_attributes = True


# ==================== ROLE PERMISSION SCHEMAS ====================

class RolePermissionCreate(BaseModel):
    """Schema for assigning a permission to a role"""
    role_id: UUID = Field(
        ...,
        description="UUID of the role to grant permission to"
    )
    permission_id: UUID = Field(
        ...,
        description="UUID of the permission to grant"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                "permission_id": "456e7890-a12b-34c5-d678-901234567890"
            }
        }


class RolePermissionResponse(BaseModel):
    """Schema for role permission response data"""
    role_id: UUID = Field(..., description="UUID of the role")
    permission_id: UUID = Field(..., description="UUID of the permission")

    class Config:
        from_attributes = True


# ==================== USER LOG SCHEMAS ====================

class UserLogCreate(BaseModel):
    """Schema for creating a user activity log entry"""
    user_id: UUID = Field(
        ...,
        description="UUID of the user who performed the action"
    )
    action: dict = Field(
        ...,
        description="JSON object containing action details (type, description, metadata)",
        examples=[{"action_type": "login", "ip_address": "192.168.1.1", "device": "Chrome Browser"}]
    )


class UserLogUpdate(BaseModel):
    """Schema for updating a user log entry"""
    action: dict = Field(
        ...,
        description="Updated action details"
    )


class UserLogResponse(BaseModel):
    """Schema for user log response data"""
    log_id: UUID = Field(..., description="Unique identifier for the log entry")
    user_id: UUID = Field(..., description="UUID of the user")
    action: dict = Field(..., description="Action details in JSON format")
    updated_at: datetime = Field(..., description="Timestamp of the log entry")

    class Config:
        from_attributes = True


# ==================== VENDOR SCHEMAS ====================

class VendorBase(BaseModel):
    """Base schema for vendor information"""
    vendor_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the vendor/supplier company",
        examples=["ABC Suppliers Pvt Ltd"]
    )
    vendor_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique vendor identification code",
        examples=["VEND001", "SUPP-2025-001"]
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Vendor contact email address"
    )
    gst_id: Optional[str] = Field(
        None,
        max_length=15,
        description="GST identification number",
        examples=["29ABCDE1234F1Z5"]
    )
    company_pan: Optional[str] = Field(
        None,
        max_length=10,
        description="PAN card number of the vendor company",
        examples=["ABCDE1234F"]
    )
    tan: Optional[str] = Field(
        None,
        max_length=10,
        description="Tax deduction account number"
    )
    bank_acc_no: Optional[str] = Field(
        None,
        max_length=20,
        description="Bank account number for payments",
        examples=["1234567890123456"]
    )
    beneficiary_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Name of the account holder as per bank records"
    )
    acc_verified: bool = Field(
        False,
        description="Whether the bank account has been verified (True/False)"
    )
    ifsc_code: Optional[str] = Field(
        None,
        max_length=11,
        description="IFSC code of the bank branch",
        examples=["SBIN0001234"]
    )
    payment_term_days: Optional[int] = Field(
        None,
        ge=0,
        le=365,
        description="Number of days for payment terms (e.g., Net 30, Net 45)",
        examples=[30, 45, 60, 90]
    )
    user_phone: Optional[str] = Field(
        None,
        max_length=15,
        description="Vendor contact phone number with country code",
        examples=["+919876543210"]
    )


class VendorCreate(VendorBase):
    """Schema for creating a new vendor"""
    class Config:
        json_schema_extra = {
            "example": {
                "vendor_name": "ABC Suppliers Pvt Ltd",
                "vendor_code": "VEND001",
                "email": "contact@abcsuppliers.com",
                "gst_id": "29ABCDE1234F1Z5",
                "company_pan": "ABCDE1234F",
                "bank_acc_no": "1234567890123456",
                "beneficiary_name": "ABC Suppliers Pvt Ltd",
                "ifsc_code": "SBIN0001234",
                "payment_term_days": 45,
                "user_phone": "+919876543210"
            }
        }


class VendorUpdate(VendorBase):
    """Schema for updating an existing vendor"""
    pass


class VendorResponse(VendorBase):
    """Schema for vendor response data"""
    vendor_id: UUID = Field(..., description="Unique identifier for the vendor")
    created_at: datetime = Field(..., description="Timestamp when vendor was created")
    updated_at: datetime = Field(..., description="Timestamp when vendor was last updated")

    class Config:
        from_attributes = True


# ==================== TRANSACTION SCHEMAS ====================

class TransactionBase(BaseModel):
    """Base schema for transaction information"""
    vendor_id: UUID = Field(
        ...,
        description="UUID of the vendor associated with this transaction"
    )
    invoice_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique invoice identifier from the vendor",
        examples=["INV-2025-001", "BILL/2025/0123"]
    )
    client_entity_id: UUID = Field(
        ...,
        description="UUID of the client entity that received goods/services"
    )
    transaction_date: date = Field(
        ...,
        description="Date when the transaction occurred",
        examples=["2025-01-15"]
    )
    transaction_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of transaction",
        examples=["Purchase", "Payment", "Refund", "Credit Note", "Debit Note"]
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Transaction amount (must be positive)",
        examples=[1000.00, 2500.50, 15000.75]
    )
    currency: str = Field(
        "INR",
        min_length=3,
        max_length=4,
        description="ISO currency code for the transaction",
        examples=["INR", "USD", "EUR", "GBP"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of goods/services in the transaction"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes, remarks, or internal comments"
    )
    status: int = Field(
        ...,
        ge=0,
        description="Transaction status code: 0=Pending, 1=Approved, 2=Rejected, 3=Processing, 4=Completed",
        examples=[0, 1, 2]
    )


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    class Config:
        json_schema_extra = {
            "example": {
                "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
                "invoice_id": "INV-2025-001",
                "client_entity_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                "transaction_date": "2025-01-15",
                "transaction_type": "Purchase",
                "amount": 15000.50,
                "currency": "INR",
                "description": "Purchase of office supplies",
                "status": 0
            }
        }


class TransactionUpdate(TransactionBase):
    """Schema for updating an existing transaction"""
    pass


class TransactionResponse(TransactionBase):
    """Schema for transaction response data"""
    transaction_id: UUID = Field(..., description="Unique identifier for the transaction")
    created_at: datetime = Field(..., description="Timestamp when transaction was created")
    updated_at: datetime = Field(..., description="Timestamp when transaction was last updated")

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


# ==================== ACTION LOG SCHEMAS ====================

class ActionLogCreate(BaseModel):
    """Schema for creating an action log entry"""
    status: int = Field(
        ...,
        ge=0,
        description="Status code of the action",
        examples=[0, 1, 2]
    )
    action: dict = Field(
        ...,
        description="JSON object containing action details",
        examples=[{"action_type": "approval", "performed_by": "admin", "timestamp": "2025-01-15T10:30:00Z"}]
    )


class ActionLogUpdate(BaseModel):
    """Schema for updating an action log entry"""
    status: int = Field(..., description="Updated status code")
    action: dict = Field(..., description="Updated action details")


class ActionLogResponse(BaseModel):
    """Schema for action log response data"""
    log_id: UUID = Field(..., description="Unique identifier for the action log")
    status: int = Field(..., description="Status code")
    action: dict = Field(..., description="Action details in JSON format")
    updated_at: datetime = Field(..., description="Timestamp of the log entry")

    class Config:
        from_attributes = True


# ==================== TRANSACTION LOG SCHEMAS ====================

class TransactionLogCreate(BaseModel):
    """Schema for creating a transaction log entry"""
    transaction_id: UUID = Field(
        ...,
        description="UUID of the transaction this log entry belongs to"
    )
    action: dict = Field(
        ...,
        description="JSON object containing log action details",
        examples=[{"action": "status_change", "from": "pending", "to": "approved"}]
    )
    approval_time: Optional[datetime] = Field(
        None,
        description="Timestamp when the transaction was approved (if applicable)"
    )
    action_log_id: Optional[UUID] = Field(
        None,
        description="Optional reference to an action log entry"
    )
    user_log_id: Optional[UUID] = Field(
        None,
        description="Optional reference to a user log entry"
    )


class TransactionLogUpdate(BaseModel):
    """Schema for updating a transaction log entry"""
    action: dict = Field(..., description="Updated action details")
    approval_time: Optional[datetime] = Field(None, description="Updated approval time")
    action_log_id: Optional[UUID] = Field(None, description="Updated action log reference")
    user_log_id: Optional[UUID] = Field(None, description="Updated user log reference")


class TransactionLogResponse(BaseModel):
    """Schema for transaction log response data"""
    log_id: UUID = Field(..., description="Unique identifier for the transaction log")
    transaction_id: UUID = Field(..., description="UUID of the associated transaction")
    action: dict = Field(..., description="Action details in JSON format")
    approval_time: Optional[datetime] = Field(None, description="Approval timestamp")
    action_log_id: Optional[UUID] = Field(None, description="Reference to action log")
    user_log_id: Optional[UUID] = Field(None, description="Reference to user log")
    updated_at: datetime = Field(..., description="Timestamp of the log entry")

    class Config:
        from_attributes = True


# ==================== ITEM SCHEMAS ====================

class ItemBase(BaseModel):
    """Base schema for item master information"""
    item_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique item code/SKU",
        examples=["ITEM001", "SKU-2025-0123"]
    )
    item_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the item/product",
        examples=["Office Chair", "Laptop - Dell Inspiron"]
    )
    hsn_code: Optional[str] = Field(
        None,
        max_length=8,
        description="HSN (Harmonized System of Nomenclature) code for tax classification",
        examples=["94013090"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the item"
    )
    unit_measurement: Optional[str] = Field(
        None,
        max_length=10,
        description="Unit of measurement for the item",
        examples=["PCS", "KG", "LITRE", "BOX", "METER"]
    )


class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    class Config:
        json_schema_extra = {
            "example": {
                "item_code": "ITEM001",
                "item_name": "Office Chair - Ergonomic",
                "hsn_code": "94013090",
                "description": "Ergonomic office chair with lumbar support",
                "unit_measurement": "PCS"
            }
        }


class ItemUpdate(ItemBase):
    """Schema for updating an existing item"""
    pass


class ItemResponse(ItemBase):
    """Schema for item response data"""
    item_id: UUID = Field(..., description="Unique identifier for the item")
    created_at: datetime = Field(..., description="Timestamp when item was created")
    updated_at: datetime = Field(..., description="Timestamp when item was last updated")

    class Config:
        from_attributes = True


# ==================== WORKFLOW SCHEMAS ====================

class WorkflowBase(BaseModel):
    """Base schema for workflow ledger information"""
    client_id: UUID = Field(
        ...,
        description="UUID of the client organization for this workflow"
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who initiated/owns this workflow"
    )
    workflow_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the workflow process",
        examples=["Invoice Approval", "Vendor Onboarding", "Payment Processing"]
    )
    request_count: int = Field(
        0,
        ge=0,
        description="Number of times this workflow has been requested/executed"
    )
    last_request_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the most recent workflow execution"
    )


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new workflow ledger"""
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                "workflow_name": "Invoice Approval Workflow",
                "request_count": 0
            }
        }


class WorkflowUpdate(WorkflowBase):
    """Schema for updating an existing workflow ledger"""
    pass


class WorkflowResponse(WorkflowBase):
    """Schema for workflow response data"""
    ledger_id: UUID = Field(..., description="Unique identifier for the workflow ledger")
    created_at: datetime = Field(..., description="Timestamp when workflow was created")
    updated_at: datetime = Field(..., description="Timestamp when workflow was last updated")

    class Config:
        from_attributes = True