from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.user_models import Users, Roles, Permissions, UserRoles, RolePermissions
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== USER CRUD ====================


@router.post("/users/create", response_model=Users)
async def create_user(user: Users, db=Depends(get_db)):
    try:
        # Check if UserID already exists
        existing = await Users.find_one(Users.UserID == user.UserID)
        if existing:
            logger.warning(f"Duplicate user creation attempt: UserID {user.UserID}")
            raise HTTPException(
                status_code=400,
                detail=f"User with UserID {user.UserID} already exists"
            )

        # Check if Email already exists
        existing_email = await Users.find_one(Users.Email == user.Email)
        if existing_email:
            logger.warning(f"Duplicate email: {user.Email}")
            raise HTTPException(
                status_code=400,
                detail=f"User with email '{user.Email}' already exists"
            )

        # Insert the user
        await user.insert()
        logger.info(f"User created successfully: {user.UserName}")
        
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users/{user_id}", response_model=Users)
async def get_user(user_id: int, db=Depends(get_db)):
    try:
        user = await Users.find_one(Users.UserID == user_id, fetch_links=True)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        
        logger.info(f"User retrieved: {user.UserName}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users", response_model=list[Users])
async def get_all_users(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        users = await Users.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(users)} users")
        return users

    except Exception as e:
        logger.error(f"Error retrieving users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/users/{user_id}", response_model=Users)
async def update_user(user_id: int, user_data: Users, db=Depends(get_db)):
    try:
        user = await Users.find_one(Users.UserID == user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        # Update fields
        user.UserName = user_data.UserName
        user.Email = user_data.Email
        user.UserPhone = user_data.UserPhone
        user.PasswordHash = user_data.PasswordHash
        user.UpdatedAt = datetime.utcnow()

        await user.save()
        logger.info(f"User updated: {user.UserName}")
        
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db)):
    try:
        user = await Users.find_one(Users.UserID == user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        await user.delete()
        logger.info(f"User deleted: {user.UserName}")
        
        return {"message": f"User {user_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")