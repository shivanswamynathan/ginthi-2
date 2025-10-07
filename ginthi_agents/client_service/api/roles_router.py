from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.user_models import Roles
from client_service.db.mongo_db import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== ROLES CRUD ====================

@router.post("/roles/create", response_model=Roles)
async def create_role(role: Roles, db=Depends(get_db)):
    try:
        # Check if RoleID already exists
        existing = await Roles.find_one(Roles.RoleID == role.RoleID)
        if existing:
            logger.warning(f"Duplicate role creation attempt: RoleID {role.RoleID}")
            raise HTTPException(
                status_code=400,
                detail=f"Role with RoleID {role.RoleID} already exists"
            )

        # Check if RoleName already exists
        existing_name = await Roles.find_one(Roles.RoleName == role.RoleName)
        if existing_name:
            logger.warning(f"Duplicate role name: {role.RoleName}")
            raise HTTPException(
                status_code=400,
                detail=f"Role with name '{role.RoleName}' already exists"
            )

        # Insert the role
        await role.insert()
        logger.info(f"Role created successfully: {role.RoleName}")
        
        return role

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/roles/{role_id}", response_model=Roles)
async def get_role(role_id: int, db=Depends(get_db)):
    try:
        role = await Roles.find_one(Roles.RoleID == role_id)
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


@router.get("/roles", response_model=list[Roles])
async def get_all_roles(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        roles = await Roles.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(roles)} roles")
        return roles

    except Exception as e:
        logger.error(f"Error retrieving roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/roles/{role_id}", response_model=Roles)
async def update_role(role_id: int, role_data: Roles, db=Depends(get_db)):
    try:
        role = await Roles.find_one(Roles.RoleID == role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_id} not found"
            )

        # Update fields
        role.RoleName = role_data.RoleName
        role.Description = role_data.Description

        await role.save()
        logger.info(f"Role updated: {role.RoleName}")
        
        return role

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, db=Depends(get_db)):
    try:
        role = await Roles.find_one(Roles.RoleID == role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role with ID {role_id} not found"
            )

        await role.delete()
        logger.info(f"Role deleted: {role.RoleName}")
        
        return {"message": f"Role {role_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")