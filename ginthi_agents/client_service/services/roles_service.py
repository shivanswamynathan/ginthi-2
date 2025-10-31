from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import Roles
from client_service.schemas.pydantic_schemas import RoleCreate, RoleUpdate, RoleResponse
from client_service.api.constants.messages import RoleMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class RoleService:
    """Service class for Role business logic"""
    
    @staticmethod
    async def create(role_data: RoleCreate, db: AsyncSession):
        """Create a new role"""
        try:
            # Check if RoleName already exists
            result = await db.execute(
                select(Roles).where(Roles.role_name == role_data.role_name)
            )
            existing_name = result.scalar_one_or_none()
            
            if existing_name:
                logger.warning(RoleMessages.DUPLICATE_NAME.format(name=role_data.role_name))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=RoleMessages.DUPLICATE_NAME.format(name=role_data.role_name)
                )

            # Create new role (UUID will be auto-generated)
            new_role = Roles(**role_data.model_dump(exclude_unset=True))
            
            db.add(new_role)
            await db.commit()
            await db.refresh(new_role)
            
            logger.info(RoleMessages.CREATED_SUCCESS.format(name=new_role.role_name))
            return APIResponse(
                success=True,
                message=RoleMessages.CREATED_SUCCESS.format(name=new_role.role_name),
                data=RoleResponse.model_validate(new_role).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(RoleMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RoleMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(role_id: UUID, db: AsyncSession):
        """Get a role by ID"""
        try:
            result = await db.execute(
                select(Roles).where(Roles.role_id == role_id)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=RoleMessages.NOT_FOUND.format(id=role_id)
                )
            
            logger.info(RoleMessages.RETRIEVED_SUCCESS.format(name=role.role_name))
            return APIResponse(
                success=True,
                message=RoleMessages.RETRIEVED_SUCCESS.format(name=role.role_name),
                data=RoleResponse.model_validate(role).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(RoleMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RoleMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all roles with pagination"""
        try:
            result = await db.execute(
                select(Roles).offset(skip).limit(limit)
            )
            roles = result.scalars().all()
            
            logger.info(RoleMessages.RETRIEVED_ALL_SUCCESS.format(count=len(roles)))
            return APIResponse(
                success=True,
                message=RoleMessages.RETRIEVED_ALL_SUCCESS.format(count=len(roles)),
                data=[RoleResponse.model_validate(role).model_dump() for role in roles]
            )

        except Exception as e:
            logger.error(RoleMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RoleMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(role_id: UUID, role_data: RoleUpdate, db: AsyncSession):
        """Update a role"""
        try:
            result = await db.execute(
                select(Roles).where(Roles.role_id == role_id)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=RoleMessages.NOT_FOUND.format(id=role_id)
                )

            # Update fields
            for key, value in role_data.model_dump(exclude_unset=True).items():
                setattr(role, key, value)

            await db.commit()
            await db.refresh(role)
            
            logger.info(RoleMessages.UPDATED_SUCCESS.format(name=role.role_name))
            return APIResponse(
                success=True,
                message=RoleMessages.UPDATED_SUCCESS.format(name=role.role_name),
                data=RoleResponse.model_validate(role).model_dump()
            )


        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(RoleMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RoleMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(role_id: UUID, db: AsyncSession):
        """Delete a role"""
        try:
            result = await db.execute(
                select(Roles).where(Roles.role_id == role_id)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=RoleMessages.NOT_FOUND.format(id=role_id)
                )

            await db.delete(role)
            await db.commit()
            
            logger.info(RoleMessages.DELETED_SUCCESS.format(id=role_id))
            return APIResponse(
                success=True,
                message=RoleMessages.DELETED_SUCCESS.format(id=role_id),
                data=None
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(RoleMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RoleMessages.DELETE_ERROR.format(error=str(e))
            )