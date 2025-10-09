from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import Users
from client_service.schemas.pydantic_schemas import UserCreate, UserUpdate
from client_service.api.constants.messages import UserMessages
from client_service.api.constants.status_codes import StatusCode
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class UserService:
    """Service class for User business logic"""
    
    @staticmethod
    async def create(user_data: UserCreate, db: AsyncSession):
        """Create a new user"""
        try:
            # Check if Email already exists
            result = await db.execute(
                select(Users).where(Users.email == user_data.email)
            )
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                logger.warning(UserMessages.DUPLICATE_EMAIL.format(email=user_data.email))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=UserMessages.DUPLICATE_EMAIL.format(email=user_data.email)
                )

            # Create new user (UUID will be auto-generated)
            new_user = Users(**user_data.model_dump(exclude_unset=True))
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(UserMessages.CREATED_SUCCESS.format(name=new_user.user_name))
            return new_user

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(UserMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(user_id: UUID, db: AsyncSession):
        """Get a user by ID"""
        try:
            result = await db.execute(
                select(Users).where(Users.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=UserMessages.NOT_FOUND.format(id=user_id)
                )
            
            logger.info(UserMessages.RETRIEVED_SUCCESS.format(name=user.user_name))
            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(UserMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all users with pagination"""
        try:
            result = await db.execute(
                select(Users).offset(skip).limit(limit)
            )
            users = result.scalars().all()
            
            logger.info(UserMessages.RETRIEVED_ALL_SUCCESS.format(count=len(users)))
            return list(users)

        except Exception as e:
            logger.error(UserMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(user_id: UUID, user_data: UserUpdate, db: AsyncSession):
        """Update a user"""
        try:
            result = await db.execute(
                select(Users).where(Users.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=UserMessages.NOT_FOUND.format(id=user_id)
                )

            # Update fields
            for key, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, key, value)
            
            user.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(user)
            
            logger.info(UserMessages.UPDATED_SUCCESS.format(name=user.user_name))
            return user

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(UserMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(user_id: UUID, db: AsyncSession):
        """Delete a user"""
        try:
            result = await db.execute(
                select(Users).where(Users.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=UserMessages.NOT_FOUND.format(id=user_id)
                )

            await db.delete(user)
            await db.commit()
            
            logger.info(UserMessages.DELETED_SUCCESS.format(id=user_id))
            return {"message": UserMessages.DELETED_SUCCESS.format(id=user_id)}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(UserMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserMessages.DELETE_ERROR.format(error=str(e))
            )