from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.user_models import RolePermissions, Roles, Permissions
from client_service.db.mongo_db import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== ROLE PERMISSIONS CRUD ====================

@router.post("/role-permissions/create", response_model=RolePermissions)
async def assign_permission_to_role(role_permission: RolePermissions, db=Depends(get_db)):
    try:
        # Check if RoleID exists
        role = await Roles.find_one(Roles.RoleID == role_permission.RoleID)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_permission.RoleID} not found"
            )

        # Check if PermissionID exists
        permission = await Permissions.find_one(
            Permissions.PermissionID == role_permission.PermissionID
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {role_permission.PermissionID} not found"
            )

        # Check if assignment already exists
        existing = await RolePermissions.find_one(
            RolePermissions.RoleID == role_permission.RoleID,
            RolePermissions.PermissionID == role_permission.PermissionID
        )
        if existing:
            logger.warning(f"Role {role_permission.RoleID} already has permission {role_permission.PermissionID}")
            raise HTTPException(
                status_code=400,
                detail=f"Role {role_permission.RoleID} already has permission {role_permission.PermissionID}"
            )

        # Insert the role permission
        await role_permission.insert()
        logger.info(f"Permission {permission.PermissionName} assigned to role {role.RoleName}")
        
        return role_permission

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning permission to role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/role-permissions/role/{role_id}", response_model=list[RolePermissions])
async def get_role_permissions(role_id: int, db=Depends(get_db)):
    try:
        role_permissions = await RolePermissions.find(
            RolePermissions.RoleID == role_id,
            fetch_links=True
        ).to_list()
        
        if not role_permissions:
            logger.info(f"No permissions found for role {role_id}")
            return []
        
        logger.info(f"Retrieved {len(role_permissions)} permissions for role {role_id}")
        return role_permissions

    except Exception as e:
        logger.error(f"Error retrieving role permissions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/role-permissions/permission/{permission_id}", response_model=list[RolePermissions])
async def get_roles_with_permission(permission_id: int, db=Depends(get_db)):
    try:
        role_permissions = await RolePermissions.find(
            RolePermissions.PermissionID == permission_id,
            fetch_links=True
        ).to_list()
        
        if not role_permissions:
            logger.info(f"No roles found with permission {permission_id}")
            return []
        
        logger.info(f"Retrieved {len(role_permissions)} roles with permission {permission_id}")
        return role_permissions

    except Exception as e:
        logger.error(f"Error retrieving permission roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/role-permissions/remove")
async def remove_permission_from_role(role_id: int, permission_id: int, db=Depends(get_db)):
    try:
        role_permission = await RolePermissions.find_one(
            RolePermissions.RoleID == role_id,
            RolePermissions.PermissionID == permission_id
        )
        if not role_permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission assignment not found for role {role_id} and permission {permission_id}"
            )

        await role_permission.delete()
        logger.info(f"Permission {permission_id} removed from role {role_id}")
        
        return {"message": f"Permission {permission_id} removed from role {role_id} successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing permission from role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")