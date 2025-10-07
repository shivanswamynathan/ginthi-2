from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.user_models import Permissions
from client_service.db.mongo_db import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== PERMISSIONS CRUD ====================

@router.post("/permissions/create", response_model=Permissions)
async def create_permission(permission: Permissions, db=Depends(get_db)):
    try:
        # Check if PermissionID already exists
        existing = await Permissions.find_one(
            Permissions.PermissionID == permission.PermissionID
        )
        if existing:
            logger.warning(f"Duplicate permission creation attempt: PermissionID {permission.PermissionID}")
            raise HTTPException(
                status_code=400,
                detail=f"Permission with PermissionID {permission.PermissionID} already exists"
            )

        # Check if PermissionName already exists
        existing_name = await Permissions.find_one(
            Permissions.PermissionName == permission.PermissionName
        )
        if existing_name:
            logger.warning(f"Duplicate permission name: {permission.PermissionName}")
            raise HTTPException(
                status_code=400,
                detail=f"Permission with name '{permission.PermissionName}' already exists"
            )

        # Insert the permission
        await permission.insert()
        logger.info(f"Permission created successfully: {permission.PermissionName}")
        
        return permission

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/permissions/{permission_id}", response_model=Permissions)
async def get_permission(permission_id: int, db=Depends(get_db)):
    try:
        permission = await Permissions.find_one(
            Permissions.PermissionID == permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {permission_id} not found"
            )
        
        logger.info(f"Permission retrieved: {permission.PermissionName}")
        return permission

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/permissions", response_model=list[Permissions])
async def get_all_permissions(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        permissions = await Permissions.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(permissions)} permissions")
        return permissions

    except Exception as e:
        logger.error(f"Error retrieving permissions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/permissions/{permission_id}", response_model=Permissions)
async def update_permission(permission_id: int, permission_data: Permissions, db=Depends(get_db)):
    try:
        permission = await Permissions.find_one(
            Permissions.PermissionID == permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {permission_id} not found"
            )

        # Update fields
        permission.PermissionName = permission_data.PermissionName
        permission.Description = permission_data.Description

        await permission.save()
        logger.info(f"Permission updated: {permission.PermissionName}")
        
        return permission

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: int, db=Depends(get_db)):
    try:
        permission = await Permissions.find_one(
            Permissions.PermissionID == permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {permission_id} not found"
            )

        await permission.delete()
        logger.info(f"Permission deleted: {permission.PermissionName}")
        
        return {"message": f"Permission {permission_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")