from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import Permissions
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import PermissionCreate, PermissionUpdate, PermissionResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/permissions/create", response_model=PermissionResponse)
async def create_permission(permission_data: PermissionCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if PermissionID already exists
        result = await db.execute(select(Permissions).where(Permissions.PermissionID == permission_data.PermissionID))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate permission creation attempt: PermissionID {permission_data.PermissionID}")
            raise HTTPException(
                status_code=400,
                detail=f"Permission with PermissionID {permission_data.PermissionID} already exists"
            )

        # Check if PermissionName already exists
        result = await db.execute(select(Permissions).where(Permissions.PermissionName == permission_data.PermissionName))
        existing_name = result.scalar_one_or_none()
        
        if existing_name:
            logger.warning(f"Duplicate permission name: {permission_data.PermissionName}")
            raise HTTPException(
                status_code=400,
                detail=f"Permission with name '{permission_data.PermissionName}' already exists"
            )

        # Create new permission
        new_permission = Permissions(**permission_data.model_dump())
        
        db.add(new_permission)
        await db.commit()
        await db.refresh(new_permission)
        
        logger.info(f"Permission created successfully: {new_permission.PermissionName}")
        return new_permission

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(permission_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Permissions).where(Permissions.PermissionID == permission_id))
        permission = result.scalar_one_or_none()
        
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


@router.get("/permissions", response_model=list[PermissionResponse])
async def get_all_permissions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Permissions).offset(skip).limit(limit))
        permissions = result.scalars().all()
        
        logger.info(f"Retrieved {len(permissions)} permissions")
        return list(permissions)

    except Exception as e:
        logger.error(f"Error retrieving permissions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(permission_id: int, permission_data: PermissionUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Permissions).where(Permissions.PermissionID == permission_id))
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {permission_id} not found"
            )

        # Update fields
        for key, value in permission_data.model_dump(exclude_unset=True).items():
            setattr(permission, key, value)

        await db.commit()
        await db.refresh(permission)
        
        logger.info(f"Permission updated: {permission.PermissionName}")
        return permission

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Permissions).where(Permissions.PermissionID == permission_id))
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission with ID {permission_id} not found"
            )

        await db.delete(permission)
        await db.commit()
        
        logger.info(f"Permission deleted: {permission.PermissionName}")
        return {"message": f"Permission {permission_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting permission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")