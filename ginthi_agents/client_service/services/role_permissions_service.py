from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import RolePermissions, Roles, Permissions
from client_service.schemas.pydantic_schemas import RolePermissionCreate, RolePermissionResponse
from client_service.api.constants.messages import RolePermissionMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class RolePermissionService:
    """Service class for RolePermission business logic"""
    
    @staticmethod
    async def assign(role_permission_data: RolePermissionCreate, db: AsyncSession):
        """Assign a permission to a role"""
        try:
            # Check if RoleID exists
            result = await db.execute(
                select(Roles).where(Roles.role_id == role_permission_data.role_id)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=RolePermissionMessages.ROLE_NOT_FOUND.format(id=role_permission_data.role_id)
                )

            # Check if PermissionID exists
            result = await db.execute(
                select(Permissions).where(Permissions.permission_id == role_permission_data.permission_id)
            )
            permission = result.scalar_one_or_none()
            
            if not permission:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=RolePermissionMessages.PERMISSION_NOT_FOUND.format(id=role_permission_data.permission_id)
                )

            # Check if assignment already exists
            result = await db.execute(
                select(RolePermissions).where(
                    RolePermissions.role_id == role_permission_data.role_id,
                    RolePermissions.permission_id == role_permission_data.permission_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.warning(
                    RolePermissionMessages.ALREADY_ASSIGNED.format(
                        role_id=role_permission_data.role_id,
                        permission_id=role_permission_data.permission_id
                    )
                )
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=RolePermissionMessages.ALREADY_ASSIGNED.format(
                        role_id=role_permission_data.role_id,
                        permission_id=role_permission_data.permission_id
                    )
                )

            # Create new role permission
            new_role_permission = RolePermissions(**role_permission_data.model_dump(exclude_unset=True))
            
            db.add(new_role_permission)
            await db.commit()
            await db.refresh(new_role_permission)
            
            logger.info(
                RolePermissionMessages.ASSIGNED_SUCCESS.format(
                    permission_name=permission.permission_name,
                    role_name=role.role_name
                )
            )
            return APIResponse(
                success=True,
                message=RolePermissionMessages.ASSIGNED_SUCCESS.format(
                    permission_name=permission.permission_name,
                    role_name=role.role_name
                ),
                data=RolePermissionResponse.model_validate(new_role_permission).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(RolePermissionMessages.ASSIGN_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RolePermissionMessages.ASSIGN_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_role_id(role_id: UUID, db: AsyncSession):
        """Get all permissions for a role"""
        try:
            result = await db.execute(
                select(RolePermissions).where(RolePermissions.role_id == role_id)
            )
            role_permissions = result.scalars().all()
            
            if not role_permissions:
                logger.info(RolePermissionMessages.NO_PERMISSIONS_FOR_ROLE.format(id=role_id))
                return []
            
            logger.info(
                RolePermissionMessages.RETRIEVED_ROLE_PERMISSIONS_SUCCESS.format(
                    count=len(role_permissions),
                    id=role_id
                )
            )
            return APIResponse(
                success=True,
                message=RolePermissionMessages.RETRIEVED_ROLE_PERMISSIONS_SUCCESS.format(
                    count=len(role_permissions),
                    id=role_id
                ),
                data=RolePermissionResponse.model_validate(role_permissions, many=True).model_dump()
            )

        except Exception as e:
            logger.error(RolePermissionMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RolePermissionMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_permission_id(permission_id: UUID, db: AsyncSession):
        """Get all roles with a permission"""
        try:
            result = await db.execute(
                select(RolePermissions).where(RolePermissions.permission_id == permission_id)
            )
            role_permissions = result.scalars().all()
            
            if not role_permissions:
                logger.info(RolePermissionMessages.NO_ROLES_FOR_PERMISSION.format(id=permission_id))
                return []
            
            logger.info(
                RolePermissionMessages.RETRIEVED_PERMISSION_ROLES_SUCCESS.format(
                    count=len(role_permissions),
                    id=permission_id
                )
            )
            return APIResponse(
                success=True,
                message=RolePermissionMessages.RETRIEVED_PERMISSION_ROLES_SUCCESS.format(
                    count=len(role_permissions),
                    id=permission_id
                ),
                data=[RolePermissionResponse.model_validate(rp).model_dump() for rp in role_permissions]
            )

        except Exception as e:
            logger.error(RolePermissionMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RolePermissionMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def remove(role_id: UUID, permission_id: UUID, db: AsyncSession):
        """Remove a permission from a role"""
        try:
            result = await db.execute(
                select(RolePermissions).where(
                    RolePermissions.role_id == role_id,
                    RolePermissions.permission_id == permission_id
                )
            )
            role_permission = result.scalar_one_or_none()
            
            if not role_permission:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=RolePermissionMessages.ASSIGNMENT_NOT_FOUND.format(
                        role_id=role_id,
                        permission_id=permission_id
                    )
                )

            await db.delete(role_permission)
            await db.commit()
            
            logger.info(
                RolePermissionMessages.REMOVED_SUCCESS.format(
                    permission_id=permission_id,
                    role_id=role_id
                )
            )
            return APIResponse(
                success=True,
                message=RolePermissionMessages.REMOVED_SUCCESS.format(
                    permission_id=permission_id,
                    role_id=role_id
                ),
                data=None
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(RolePermissionMessages.REMOVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=RolePermissionMessages.REMOVE_ERROR.format(error=str(e))
            )