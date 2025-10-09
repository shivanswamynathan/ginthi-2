from fastapi import APIRouter, Depends
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


@router.post("/roles/create", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new role"""
    return await RoleService.create(role_data, db)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a role by ID"""
    return await RoleService.get_by_id(role_id, db)


@router.get("/roles", response_model=list[RoleResponse])
async def get_all_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all roles with pagination"""
    return await RoleService.get_all(skip, limit, db)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a role"""
    return await RoleService.update(role_id, role_data, db)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a role"""
    return await RoleService.delete(role_id, db)