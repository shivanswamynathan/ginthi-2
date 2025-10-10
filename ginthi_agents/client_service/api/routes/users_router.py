from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.users_service import UserService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/users/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user account with name, email, and associates with a client organization.",
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new user with name, email, client_id, and password."""
    return await UserService.create(user_data, db)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieves user details by UUID. Use when: 'get user details', 'show user', 'find user'.",
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a user by ID"""
    return await UserService.get_by_id(user_id, db)


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List all users",
    description="Get paginated list of all users. Use when: 'list users', 'show all users', 'get users'.",
)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all users with pagination"""
    return await UserService.get_all(skip, limit, db)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user information",
    description="Updates user name, email, phone, or password. Use when: 'update user', 'modify user', 'change user details'.",
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a user"""
    return await UserService.update(user_id, user_data, db)


@router.delete(
    "/users/{user_id}",
    summary="Delete user",
    description="Permanently deletes a user. Use when: 'delete user', 'remove user', 'deactivate user'.",
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a user"""
    return await UserService.delete(user_id, db)