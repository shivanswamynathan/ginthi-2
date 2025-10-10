from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.roles_service import RoleService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    RoleCreate,
    RoleUpdate,
    RoleResponse
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/roles/create",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create role",
    description="Creates a new user role. Use when: 'create role', 'add role', 'define new role'.",
)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new role"""
    return await RoleService.create(role_data, db)


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Get role by ID",
    description="Retrieves role details. Use when: 'get role', 'show role', 'find role'.",
)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a role by ID"""
    return await RoleService.get_by_id(role_id, db)


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="List all roles",
    description="Get all roles with pagination. Use when: 'list roles', 'show all roles'.",
)
async def get_all_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all roles with pagination"""
    return await RoleService.get_all(skip, limit, db)


@router.put(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Update role",
    description="Updates role name/description. Use when: 'update role', 'modify role'.",
)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a role"""
    return await RoleService.update(role_id, role_data, db)


@router.delete(
    "/roles/{role_id}",
    summary="Delete role",
    description="Deletes a role. Use when: 'delete role', 'remove role'.",
)
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a role"""
    return await RoleService.delete(role_id, db)