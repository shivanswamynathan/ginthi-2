from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.permissions_service import PermissionService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/permissions/create",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
    description="Creates a new permission. Use when: 'create permission', 'add permission', 'define permission'.",
)
async def create_permission(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new permission"""
    return await PermissionService.create(permission_data, db)


@router.get(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Get permission by ID",
    description="Retrieves permission details. Use when: 'get permission', 'show permission'.",
)
async def get_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a permission by ID"""
    return await PermissionService.get_by_id(permission_id, db)


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    summary="List all permissions",
    description="Get all permissions with pagination. Use when: 'list permissions', 'show all permissions'.",
)
async def get_all_permissions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all permissions with pagination"""
    return await PermissionService.get_all(skip, limit, db)


@router.put(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Update permission",
    description="Updates permission details. Use when: 'update permission', 'modify permission'.",
)
async def update_permission(
    permission_id: UUID,
    permission_data: PermissionUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a permission"""
    return await PermissionService.update(permission_id, permission_data, db)


@router.delete(
    "/permissions/{permission_id}",
    summary="Delete permission",
    description="Deletes a permission. Use when: 'delete permission', 'remove permission'.",
)
async def delete_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a permission"""
    return await PermissionService.delete(permission_id, db)