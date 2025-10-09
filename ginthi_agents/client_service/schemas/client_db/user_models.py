from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime, timezone
import uuid
from client_service.db.postgres_db import Base


class Roles(Base):
    __tablename__ = "roles"

    RoleID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    RoleName = Column(String(50), nullable=False, unique=True)
    Description = Column(Text, nullable=True)

    # Relationships
    user_roles = relationship("UserRoles", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermissions", back_populates="role", cascade="all, delete-orphan")


class Permissions(Base):
    __tablename__ = "permissions"

    PermissionID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    PermissionName = Column(String(100), nullable=False, unique=True)
    Description = Column(Text, nullable=True)

    # Relationships
    role_permissions = relationship("RolePermissions", back_populates="permission", cascade="all, delete-orphan")


class RolePermissions(Base):
    __tablename__ = "role_permissions"

    RoleID = Column(UUID(as_uuid=True), ForeignKey("roles.RoleID"), primary_key=True)
    PermissionID = Column(UUID(as_uuid=True), ForeignKey("permissions.PermissionID"), primary_key=True)

    # Relationships
    role = relationship("Roles", back_populates="role_permissions")
    permission = relationship("Permissions", back_populates="role_permissions")


class Users(Base):
    __tablename__ = "users"

    UserID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ClientID = Column(UUID(as_uuid=True), ForeignKey("clients.ClientID"), nullable=False, index=True)
    UserName = Column(String(100), nullable=False)
    Email = Column(String(255), nullable=False, unique=True)
    UserPhone = Column(String(13), nullable=True)
    PasswordHash = Column(String(255), nullable=False)
    CreatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    client = relationship("Clients", back_populates="users")
    user_roles = relationship("UserRoles", back_populates="user", cascade="all, delete-orphan")
    user_logs = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("WorkflowRequestLedger", back_populates="user", cascade="all, delete-orphan")


class UserRoles(Base):
    __tablename__ = "user_roles"

    UserID = Column(UUID(as_uuid=True), ForeignKey("users.UserID"), primary_key=True)
    RoleID = Column(UUID(as_uuid=True), ForeignKey("roles.RoleID"), primary_key=True)
    AssignedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("Users", back_populates="user_roles")
    role = relationship("Roles", back_populates="user_roles")


class UserLog(Base):
    __tablename__ = "user_log"

    LogId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    UserID = Column(UUID(as_uuid=True), ForeignKey("users.UserID"), nullable=False, index=True)
    Action = Column(JSONB, nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("Users", back_populates="user_logs")