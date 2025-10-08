from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.item_models import ItemMaster
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import ItemCreate, ItemUpdate, ItemResponse
import logging
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/items/create", response_model=ItemResponse)
async def create_item(item_data: ItemCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if ItemID already exists
        result = await db.execute(select(ItemMaster).where(ItemMaster.ItemID == item_data.ItemID))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate item creation attempt: ItemID {item_data.ItemID}")
            raise HTTPException(
                status_code=400,
                detail=f"Item with ItemID {item_data.ItemID} already exists"
            )

        # Check if ItemCode already exists
        result = await db.execute(select(ItemMaster).where(ItemMaster.ItemCode == item_data.ItemCode))
        existing_code = result.scalar_one_or_none()
        
        if existing_code:
            logger.warning(f"Duplicate item code: {item_data.ItemCode}")
            raise HTTPException(
                status_code=400,
                detail=f"Item with code '{item_data.ItemCode}' already exists"
            )

        # Create new item
        new_item = ItemMaster(**item_data.model_dump())
        
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        
        logger.info(f"Item created successfully: {new_item.ItemName}")
        return new_item

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ItemMaster).where(ItemMaster.ItemID == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {item_id} not found"
            )
        
        logger.info(f"Item retrieved: {item.ItemName}")
        return item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/items", response_model=list[ItemResponse])
async def get_all_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ItemMaster).offset(skip).limit(limit))
        items = result.scalars().all()
        
        logger.info(f"Retrieved {len(items)} items")
        return list(items)

    except Exception as e:
        logger.error(f"Error retrieving items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/items/search/{item_code}", response_model=ItemResponse)
async def get_item_by_code(item_code: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ItemMaster).where(ItemMaster.ItemCode == item_code))
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with code '{item_code}' not found"
            )
        
        logger.info(f"Item retrieved by code: {item.ItemName}")
        return item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving item by code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_data: ItemUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ItemMaster).where(ItemMaster.ItemID == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {item_id} not found"
            )

        # Update fields
        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        
        item.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(item)
        
        logger.info(f"Item updated: {item.ItemName}")
        return item

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ItemMaster).where(ItemMaster.ItemID == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {item_id} not found"
            )

        await db.delete(item)
        await db.commit()
        
        logger.info(f"Item deleted: {item.ItemName}")
        return {"message": f"Item {item_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")