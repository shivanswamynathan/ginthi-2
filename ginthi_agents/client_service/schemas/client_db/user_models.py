from beanie import Document, Link
from pydantic import Field, EmailStr
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from client_service.schemas.client_db.client_models import Clients

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
    
    role: Optional[Link[Roles]] = None
    permission: Optional[Link[Permissions]] = None

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
    

    client: Optional[Link["Clients"]] = None

    class Settings:
        name = "users"


class UserRoles(Document):
    UserID: int
    RoleID: int
    AssignedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships: UserRoles -> Users (1) and Roles (1)
    user: Optional[Link[Users]] = None
    role: Optional[Link[Roles]] = None

    class Settings:
        name = "user_roles"


class UserLog(Document):
    LogId: int
    UserID: int
    Action: dict
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationship: UserLog -> Users (1)
    user: Optional[Link[Users]] = None

    class Settings:
        name = "user_log"