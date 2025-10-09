from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import Users
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import UserCreate, UserUpdate, UserResponse
import logging
from datetime import datetime, timezone
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/users/create", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        
        # Check if Email already exists
        result = await db.execute(select(Users).where(Users.Email == user_data.Email))
        existing_email = result.scalar_one_or_none()
        
        if existing_email:
            logger.warning(f"Duplicate email: {user_data.Email}")
            raise HTTPException(
                status_code=400,
                detail=f"User with email '{user_data.Email}' already exists"
            )

        # Create new user
        new_user = Users(**user_data.model_dump(exclude_unset=True))
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"User created successfully: {new_user.UserName}")
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Users).where(Users.UserID == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        
        logger.info(f"User retrieved: {user.UserName}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Users).offset(skip).limit(limit))
        users = result.scalars().all()
        
        logger.info(f"Retrieved {len(users)} users")
        return list(users)

    except Exception as e:
        logger.error(f"Error retrieving users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Users).where(Users.UserID == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        # Update fields
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        
        user.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User updated: {user.UserName}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/users/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Users).where(Users.UserID == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        await db.delete(user)
        await db.commit()
        
        logger.info(f"User deleted: {user.UserName}")
        return {"message": f"User {user_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")