from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
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

class Users(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    UserID: int
    ClientID: int
    UserName: str
    Email: EmailStr
    UserPhone: Optional[str] = None
    PasswordHash: str
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Roles(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    RoleID: int
    RoleName: str
    Description: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Permissions(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    PermissionID: int
    PermissionName: str
    Description: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserRoles(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    UserID: int
    RoleID: int
    AssignedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class RolePermissions(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    RoleID: int
    PermissionID: int

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    LogId: int
    UserID: int
    Action: dict  # JSONB in PostgreSQL = dict in MongoDB
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}