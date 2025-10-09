from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.user_roles_service import UserRoleService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import UserRoleCreate, UserRoleResponse
from uuid import UUID

router = APIRouter()


@router.post("/user-roles/create", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_role_data: UserRoleCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Assign a role to a user"""
    return await UserRoleService.assign(user_role_data, db)


@router.get("/user-roles/user/{user_id}", response_model=list[UserRoleResponse])
async def get_user_roles(
    user_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all roles for a user"""
    return await UserRoleService.get_by_user_id(user_id, db)


@router.get("/user-roles/role/{role_id}", response_model=list[UserRoleResponse])
async def get_users_with_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all users with a role"""
    return await UserRoleService.get_by_role_id(role_id, db)


@router.delete("/user-roles/remove")
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Remove a role from a user"""
    return await UserRoleService.remove(user_id, role_id, db)