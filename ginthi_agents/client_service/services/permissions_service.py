from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import Permissions
from client_service.schemas.pydantic_schemas import PermissionCreate, PermissionUpdate, PermissionResponse
from client_service.api.constants.messages import PermissionMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class PermissionService:
    """Service class for Permission business logic"""
    
    @staticmethod
    async def create(permission_data: PermissionCreate, db: AsyncSession):
        """Create a new permission"""
        try:
            # Check if PermissionName already exists
            result = await db.execute(
                select(Permissions).where(Permissions.permission_name == permission_data.permission_name)
            )
            existing_name = result.scalar_one_or_none()
            
            if existing_name:
                logger.warning(PermissionMessages.DUPLICATE_NAME.format(name=permission_data.permission_name))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=PermissionMessages.DUPLICATE_NAME.format(name=permission_data.permission_name)
                )

            # Create new permission (UUID will be auto-generated)
            new_permission = Permissions(**permission_data.model_dump(exclude_unset=True))
            
            db.add(new_permission)
            await db.commit()
            await db.refresh(new_permission)
            
            logger.info(PermissionMessages.CREATED_SUCCESS.format(name=new_permission.permission_name))
            return APIResponse(
                success=True,
                message=PermissionMessages.CREATED_SUCCESS.format(name=new_permission.permission_name),
                data=PermissionResponse.model_validate(new_permission).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(PermissionMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=PermissionMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(permission_id: UUID, db: AsyncSession):
        """Get a permission by ID"""
        try:
            result = await db.execute(
                select(Permissions).where(Permissions.permission_id == permission_id)
            )
            permission = result.scalar_one_or_none()
            
            if not permission:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=PermissionMessages.NOT_FOUND.format(id=permission_id)
                )
            
            logger.info(PermissionMessages.RETRIEVED_SUCCESS.format(name=permission.permission_name))
            return APIResponse(
                success=True,
                message=PermissionMessages.RETRIEVED_SUCCESS.format(name=permission.permission_name),
                data=PermissionResponse.model_validate(permission).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(PermissionMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=PermissionMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all permissions with pagination"""
        try:
            result = await db.execute(
                select(Permissions).offset(skip).limit(limit)
            )
            permissions = result.scalars().all()
            
            logger.info(PermissionMessages.RETRIEVED_ALL_SUCCESS.format(count=len(permissions)))
            return APIResponse(
                success=True,
                message=PermissionMessages.RETRIEVED_ALL_SUCCESS.format(count=len(permissions)),
                data=[PermissionResponse.model_validate(perm).model_dump() for perm in permissions]
            )

        except Exception as e:
            logger.error(PermissionMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=PermissionMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(permission_id: UUID, permission_data: PermissionUpdate, db: AsyncSession):
        """Update a permission"""
        try:
            result = await db.execute(
                select(Permissions).where(Permissions.permission_id == permission_id)
            )
            permission = result.scalar_one_or_none()
            
            if not permission:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=PermissionMessages.NOT_FOUND.format(id=permission_id)
                )

            # Update fields
            for key, value in permission_data.model_dump(exclude_unset=True).items():
                setattr(permission, key, value)

            await db.commit()
            await db.refresh(permission)
            
            logger.info(PermissionMessages.UPDATED_SUCCESS.format(name=permission.permission_name))
            return APIResponse(
                success=True,
                message=PermissionMessages.UPDATED_SUCCESS.format(name=permission.permission_name),
                data=PermissionResponse.model_validate(permission).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(PermissionMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=PermissionMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(permission_id: UUID, db: AsyncSession):
        """Delete a permission"""
        try:
            result = await db.execute(
                select(Permissions).where(Permissions.permission_id == permission_id)
            )
            permission = result.scalar_one_or_none()
            
            if not permission:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=PermissionMessages.NOT_FOUND.format(id=permission_id)
                )

            await db.delete(permission)
            await db.commit()
            
            logger.info(PermissionMessages.DELETED_SUCCESS.format(id=permission_id))
            return APIResponse(
                success=True,
                message=PermissionMessages.DELETED_SUCCESS.format(id=permission_id),
                data=None
            )
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(PermissionMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=PermissionMessages.DELETE_ERROR.format(error=str(e))
            )