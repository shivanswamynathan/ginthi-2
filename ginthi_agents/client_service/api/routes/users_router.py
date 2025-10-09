from fastapi import APIRouter, Depends
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


@router.post("/users/create", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new user"""
    return await UserService.create(user_data, db)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a user by ID"""
    return await UserService.get_by_id(user_id, db)


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all users with pagination"""
    return await UserService.get_all(skip, limit, db)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a user"""
    return await UserService.update(user_id, user_data, db)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a user"""
    return await UserService.delete(user_id, db)