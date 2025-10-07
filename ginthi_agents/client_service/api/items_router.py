from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.item_models import ItemMaster
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== ITEM MASTER CRUD ====================

@router.post("/items/create", response_model=ItemMaster)
async def create_item(item: ItemMaster, db=Depends(get_db)):
    try:
        # Check if ItemID already exists
        existing = await ItemMaster.find_one(ItemMaster.ItemID == item.ItemID)
        if existing:
            logger.warning(f"Duplicate item creation attempt: ItemID {item.ItemID}")
            raise HTTPException(
                status_code=400,
                detail=f"Item with ItemID {item.ItemID} already exists"
            )

        # Check if ItemCode already exists
        existing_code = await ItemMaster.find_one(ItemMaster.ItemCode == item.ItemCode)
        if existing_code:
            logger.warning(f"Duplicate item code: {item.ItemCode}")
            raise HTTPException(
                status_code=400,
                detail=f"Item with code '{item.ItemCode}' already exists"
            )

        # Insert the item
        await item.insert()
        logger.info(f"Item created successfully: {item.ItemName}")
        
        return item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/items/{item_id}", response_model=ItemMaster)
async def get_item(item_id: int, db=Depends(get_db)):
    try:
        item = await ItemMaster.find_one(ItemMaster.ItemID == item_id)
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


@router.get("/items", response_model=list[ItemMaster])
async def get_all_items(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        items = await ItemMaster.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(items)} items")
        return items

    except Exception as e:
        logger.error(f"Error retrieving items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/items/search/{item_code}", response_model=ItemMaster)
async def get_item_by_code(item_code: str, db=Depends(get_db)):
    try:
        item = await ItemMaster.find_one(ItemMaster.ItemCode == item_code)
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


@router.put("/items/{item_id}", response_model=ItemMaster)
async def update_item(item_id: int, item_data: ItemMaster, db=Depends(get_db)):
    try:
        item = await ItemMaster.find_one(ItemMaster.ItemID == item_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {item_id} not found"
            )

        # Update fields
        item.ItemCode = item_data.ItemCode
        item.ItemName = item_data.ItemName
        item.HSNCode = item_data.HSNCode
        item.Description = item_data.Description
        item.UnitMeasurement = item_data.UnitMeasurement
        item.UpdatedAt = datetime.utcnow()

        await item.save()
        logger.info(f"Item updated: {item.ItemName}")
        
        return item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db=Depends(get_db)):
    try:
        item = await ItemMaster.find_one(ItemMaster.ItemID == item_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {item_id} not found"
            )

        await item.delete()
        logger.info(f"Item deleted: {item.ItemName}")
        
        return {"message": f"Item {item_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")