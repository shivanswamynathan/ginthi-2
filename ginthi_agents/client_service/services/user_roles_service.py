from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import UserRoles, Users, Roles
from client_service.schemas.pydantic_schemas import UserRoleCreate
from client_service.api.constants.messages import UserRoleMessages
from client_service.api.constants.status_codes import StatusCode
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class UserRoleService:
    """Service class for UserRole business logic"""
    
    @staticmethod
    async def assign(user_role_data: UserRoleCreate, db: AsyncSession):
        """Assign a role to a user"""
        try:
            # Check if UserID exists
            result = await db.execute(
                select(Users).where(Users.user_id == user_role_data.user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=UserRoleMessages.USER_NOT_FOUND.format(id=user_role_data.user_id)
                )

            # Check if RoleID exists
            result = await db.execute(
                select(Roles).where(Roles.role_id == user_role_data.role_id)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=UserRoleMessages.ROLE_NOT_FOUND.format(id=user_role_data.role_id)
                )

            # Check if assignment already exists
            result = await db.execute(
                select(UserRoles).where(
                    UserRoles.user_id == user_role_data.user_id,
                    UserRoles.role_id == user_role_data.role_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.warning(
                    UserRoleMessages.ALREADY_ASSIGNED.format(
                        user_id=user_role_data.user_id,
                        role_id=user_role_data.role_id
                    )
                )
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=UserRoleMessages.ALREADY_ASSIGNED.format(
                        user_id=user_role_data.user_id,
                        role_id=user_role_data.role_id
                    )
                )

            # Create new user role
            new_user_role = UserRoles(**user_role_data.model_dump(exclude_unset=True))
            
            db.add(new_user_role)
            await db.commit()
            await db.refresh(new_user_role)
            
            logger.info(
                UserRoleMessages.ASSIGNED_SUCCESS.format(
                    role_name=role.role_name,
                    user_name=user.user_name
                )
            )
            return new_user_role

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(UserRoleMessages.ASSIGN_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserRoleMessages.ASSIGN_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_user_id(user_id: UUID, db: AsyncSession):
        """Get all roles for a user"""
        try:
            result = await db.execute(
                select(UserRoles).where(UserRoles.user_id == user_id)
            )
            user_roles = result.scalars().all()
            
            if not user_roles:
                logger.info(UserRoleMessages.NO_ROLES_FOR_USER.format(id=user_id))
                return []
            
            logger.info(
                UserRoleMessages.RETRIEVED_USER_ROLES_SUCCESS.format(
                    count=len(user_roles),
                    id=user_id
                )
            )
            return list(user_roles)

        except Exception as e:
            logger.error(UserRoleMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserRoleMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_role_id(role_id: UUID, db: AsyncSession):
        """Get all users with a role"""
        try:
            result = await db.execute(
                select(UserRoles).where(UserRoles.role_id == role_id)
            )
            user_roles = result.scalars().all()
            
            if not user_roles:
                logger.info(UserRoleMessages.NO_USERS_FOR_ROLE.format(id=role_id))
                return []
            
            logger.info(
                UserRoleMessages.RETRIEVED_ROLE_USERS_SUCCESS.format(
                    count=len(user_roles),
                    id=role_id
                )
            )
            return list(user_roles)

        except Exception as e:
            logger.error(UserRoleMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserRoleMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def remove(user_id: UUID, role_id: UUID, db: AsyncSession):
        """Remove a role from a user"""
        try:
            result = await db.execute(
                select(UserRoles).where(
                    UserRoles.user_id == user_id,
                    UserRoles.role_id == role_id
                )
            )
            user_role = result.scalar_one_or_none()
            
            if not user_role:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=UserRoleMessages.ASSIGNMENT_NOT_FOUND.format(
                        user_id=user_id,
                        role_id=role_id
                    )
                )

            await db.delete(user_role)
            await db.commit()
            
            logger.info(
                UserRoleMessages.REMOVED_SUCCESS.format(
                    role_id=role_id,
                    user_id=user_id
                )
            )
            return {
                "message": UserRoleMessages.REMOVED_SUCCESS.format(
                    role_id=role_id,
                    user_id=user_id
                )
            }

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(UserRoleMessages.REMOVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=UserRoleMessages.REMOVE_ERROR.format(error=str(e))
            )