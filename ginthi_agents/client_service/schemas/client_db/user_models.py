from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime, timezone


class Roles(Document):
    RoleID: int
    RoleName: str
    Description: Optional[str] = None

    class Settings:
        name = "roles"


class Permissions(Document):
    PermissionID: int
    PermissionName: str
    Description: Optional[str] = None

    class Settings:
        name = "permissions"


class RolePermissions(Document):
    RoleID: int
    PermissionID: int
    class Settings:
        name = "role_permissions"


class Users(Document):
    UserID: int
    ClientID: int
    UserName: str
    Email: EmailStr
    UserPhone: Optional[str] = None
    PasswordHash: str
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "users"


class UserRoles(Document):
    UserID: int
    RoleID: int
    AssignedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "user_roles"


class UserLog(Document):
    LogId: int
    UserID: int
    Action: dict
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    

    class Settings:
        name = "user_log"