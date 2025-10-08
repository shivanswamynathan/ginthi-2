from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import UserRoles, Users, Roles
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import UserRoleCreate, UserRoleResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/user-roles/create", response_model=UserRoleResponse)
async def assign_role_to_user(user_role_data: UserRoleCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if UserID exists
        result = await db.execute(select(Users).where(Users.UserID == user_role_data.UserID))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_role_data.UserID} not found"
            )

        # Check if RoleID exists
        result = await db.execute(select(Roles).where(Roles.RoleID == user_role_data.RoleID))
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {user_role_data.RoleID} not found"
            )

        # Check if assignment already exists
        result = await db.execute(
            select(UserRoles).where(
                UserRoles.UserID == user_role_data.UserID,
                UserRoles.RoleID == user_role_data.RoleID
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"User {user_role_data.UserID} already has role {user_role_data.RoleID}")
            raise HTTPException(
                status_code=400,
                detail=f"User {user_role_data.UserID} already has role {user_role_data.RoleID}"
            )

        # Create new user role
        new_user_role = UserRoles(**user_role_data.model_dump())
        
        db.add(new_user_role)
        await db.commit()
        await db.refresh(new_user_role)
        
        logger.info(f"Role {role.RoleName} assigned to user {user.UserName}")
        return new_user_role

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error assigning role to user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-roles/user/{user_id}", response_model=list[UserRoleResponse])
async def get_user_roles(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(UserRoles).where(UserRoles.UserID == user_id))
        user_roles = result.scalars().all()
        
        if not user_roles:
            logger.info(f"No roles found for user {user_id}")
            return []
        
        logger.info(f"Retrieved {len(user_roles)} roles for user {user_id}")
        return list(user_roles)

    except Exception as e:
        logger.error(f"Error retrieving user roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-roles/role/{role_id}", response_model=list[UserRoleResponse])
async def get_users_with_role(role_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(UserRoles).where(UserRoles.RoleID == role_id))
        user_roles = result.scalars().all()
        
        if not user_roles:
            logger.info(f"No users found with role {role_id}")
            return []
        
        logger.info(f"Retrieved {len(user_roles)} users with role {role_id}")
        return list(user_roles)

    except Exception as e:
        logger.error(f"Error retrieving role users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/user-roles/remove")
async def remove_role_from_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(UserRoles).where(
                UserRoles.UserID == user_id,
                UserRoles.RoleID == role_id
            )
        )
        user_role = result.scalar_one_or_none()
        
        if not user_role:
            raise HTTPException(
                status_code=404,
                detail=f"Role assignment not found for user {user_id} and role {role_id}"
            )

        await db.delete(user_role)
        await db.commit()
        
        logger.info(f"Role {role_id} removed from user {user_id}")
        return {"message": f"Role {role_id} removed from user {user_id} successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error removing role from user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")