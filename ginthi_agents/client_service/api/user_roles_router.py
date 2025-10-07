from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.user_models import UserRoles, Users, Roles
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== USER ROLES CRUD ====================

@router.post("/user-roles/create", response_model=UserRoles)
async def assign_role_to_user(user_role: UserRoles, db=Depends(get_db)):
    try:
        # Check if UserID exists
        user = await Users.find_one(Users.UserID == user_role.UserID)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_role.UserID} not found"
            )

        # Check if RoleID exists
        role = await Roles.find_one(Roles.RoleID == user_role.RoleID)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {user_role.RoleID} not found"
            )

        # Check if assignment already exists
        existing = await UserRoles.find_one(
            UserRoles.UserID == user_role.UserID,
            UserRoles.RoleID == user_role.RoleID
        )
        if existing:
            logger.warning(f"User {user_role.UserID} already has role {user_role.RoleID}")
            raise HTTPException(
                status_code=400,
                detail=f"User {user_role.UserID} already has role {user_role.RoleID}"
            )

        # Insert the user role
        await user_role.insert()
        logger.info(f"Role {role.RoleName} assigned to user {user.UserName}")
        
        return user_role

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning role to user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-roles/user/{user_id}", response_model=list[UserRoles])
async def get_user_roles(user_id: int, db=Depends(get_db)):
    try:
        user_roles = await UserRoles.find(
            UserRoles.UserID == user_id,
            fetch_links=True
        ).to_list()
        
        if not user_roles:
            logger.info(f"No roles found for user {user_id}")
            return []
        
        logger.info(f"Retrieved {len(user_roles)} roles for user {user_id}")
        return user_roles

    except Exception as e:
        logger.error(f"Error retrieving user roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-roles/role/{role_id}", response_model=list[UserRoles])
async def get_users_with_role(role_id: int, db=Depends(get_db)):
    try:
        user_roles = await UserRoles.find(
            UserRoles.RoleID == role_id,
            fetch_links=True
        ).to_list()
        
        if not user_roles:
            logger.info(f"No users found with role {role_id}")
            return []
        
        logger.info(f"Retrieved {len(user_roles)} users with role {role_id}")
        return user_roles

    except Exception as e:
        logger.error(f"Error retrieving role users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/user-roles/remove")
async def remove_role_from_user(user_id: int, role_id: int, db=Depends(get_db)):
    try:
        user_role = await UserRoles.find_one(
            UserRoles.UserID == user_id,
            UserRoles.RoleID == role_id
        )
        if not user_role:
            raise HTTPException(
                status_code=404,
                detail=f"Role assignment not found for user {user_id} and role {role_id}"
            )

        await user_role.delete()
        logger.info(f"Role {role_id} removed from user {user_id}")
        
        return {"message": f"Role {role_id} removed from user {user_id} successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing role from user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")