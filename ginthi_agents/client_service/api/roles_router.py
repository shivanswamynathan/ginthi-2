from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.user_models import Roles
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import RoleCreate, RoleUpdate, RoleResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/roles/create", response_model=RoleResponse)
async def create_role(role_data: RoleCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if RoleID already exists
        result = await db.execute(select(Roles).where(Roles.RoleID == role_data.RoleID))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate role creation attempt: RoleID {role_data.RoleID}")
            raise HTTPException(
                status_code=400,
                detail=f"Role with RoleID {role_data.RoleID} already exists"
            )

        # Check if RoleName already exists
        result = await db.execute(select(Roles).where(Roles.RoleName == role_data.RoleName))
        existing_name = result.scalar_one_or_none()
        
        if existing_name:
            logger.warning(f"Duplicate role name: {role_data.RoleName}")
            raise HTTPException(
                status_code=400,
                detail=f"Role with name '{role_data.RoleName}' already exists"
            )

        # Create new role
        new_role = Roles(**role_data.model_dump())
        
        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)
        
        logger.info(f"Role created successfully: {new_role.RoleName}")
        return new_role

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Roles).where(Roles.RoleID == role_id))
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_id} not found"
            )
        
        logger.info(f"Role retrieved: {role.RoleName}")
        return role

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/roles", response_model=list[RoleResponse])
async def get_all_roles(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Roles).offset(skip).limit(limit))
        roles = result.scalars().all()
        
        logger.info(f"Retrieved {len(roles)} roles")
        return list(roles)

    except Exception as e:
        logger.error(f"Error retrieving roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role_data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Roles).where(Roles.RoleID == role_id))
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_id} not found"
            )

        # Update fields
        for key, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, key, value)

        await db.commit()
        await db.refresh(role)
        
        logger.info(f"Role updated: {role.RoleName}")
        return role

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Roles).where(Roles.RoleID == role_id))
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_id} not found"
            )

        await db.delete(role)
        await db.commit()
        
        logger.info(f"Role deleted: {role.RoleName}")
        return {"message": f"Role {role_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")