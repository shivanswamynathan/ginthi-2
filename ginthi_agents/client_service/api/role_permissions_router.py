from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import RolePermissions, Roles, Permissions
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import RolePermissionCreate, RolePermissionResponse
import logging
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/role-permissions/create", response_model=RolePermissionResponse)
async def assign_permission_to_role(role_permission_data: RolePermissionCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if RoleID exists
        result = await db.execute(select(Roles).where(Roles.RoleID == role_permission_data.RoleID))
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_permission_data.RoleID} not found"
            )

        # Check if PermissionID exists
        result = await db.execute(select(Permissions).where(Permissions.PermissionID == role_permission_data.PermissionID))
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {role_permission_data.PermissionID} not found"
            )

        # Check if assignment already exists
        result = await db.execute(
            select(RolePermissions).where(
                RolePermissions.RoleID == role_permission_data.RoleID,
                RolePermissions.PermissionID == role_permission_data.PermissionID
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Role {role_permission_data.RoleID} already has permission {role_permission_data.PermissionID}")
            raise HTTPException(
                status_code=400,
                detail=f"Role {role_permission_data.RoleID} already has permission {role_permission_data.PermissionID}"
            )

        # Create new role permission
        new_role_permission = RolePermissions(**role_permission_data.model_dump(exclude_unset=True))
        
        db.add(new_role_permission)
        await db.commit()
        await db.refresh(new_role_permission)
        
        logger.info(f"Permission {permission.PermissionName} assigned to role {role.RoleName}")
        return new_role_permission

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error assigning permission to role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/role-permissions/role/{role_id}", response_model=list[RolePermissionResponse])
async def get_role_permissions(role_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(RolePermissions).where(RolePermissions.RoleID == role_id))
        role_permissions = result.scalars().all()
        
        if not role_permissions:
            logger.info(f"No permissions found for role {role_id}")
            return []
        
        logger.info(f"Retrieved {len(role_permissions)} permissions for role {role_id}")
        return list(role_permissions)

    except Exception as e:
        logger.error(f"Error retrieving role permissions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/role-permissions/permission/{permission_id}", response_model=list[RolePermissionResponse])
async def get_roles_with_permission(permission_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(RolePermissions).where(RolePermissions.PermissionID == permission_id))
        role_permissions = result.scalars().all()
        
        if not role_permissions:
            logger.info(f"No roles found with permission {permission_id}")
            return []
        
        logger.info(f"Retrieved {len(role_permissions)} roles with permission {permission_id}")
        return list(role_permissions)

    except Exception as e:
        logger.error(f"Error retrieving permission roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/role-permissions/remove")
async def remove_permission_from_role(role_id: UUID, permission_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(RolePermissions).where(
                RolePermissions.RoleID == role_id,
                RolePermissions.PermissionID == permission_id
            )
        )
        role_permission = result.scalar_one_or_none()
        
        if not role_permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission assignment not found for role {role_id} and permission {permission_id}"
            )

        await db.delete(role_permission)
        await db.commit()
        
        logger.info(f"Permission {permission_id} removed from role {role_id}")
        return {"message": f"Permission {permission_id} removed from role {role_id} successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error removing permission from role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")