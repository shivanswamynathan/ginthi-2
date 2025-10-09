from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.items_service import ItemService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    ItemCreate,
    ItemUpdate,
    ItemResponse
)
from uuid import UUID

router = APIRouter()


@router.post("/items/create", response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new item"""
    return await ItemService.create(item_data, db)


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get an item by ID"""
    return await ItemService.get_by_id(item_id, db)


@router.get("/items", response_model=list[ItemResponse])
async def get_all_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all items with pagination"""
    return await ItemService.get_all(skip, limit, db)


@router.get("/items/search/{item_code}", response_model=ItemResponse)
async def get_item_by_code(
    item_code: str,
    db: AsyncSession = Depends(get_database_session)
):
    """Get an item by code"""
    return await ItemService.get_by_code(item_code, db)


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update an item"""
    return await ItemService.update(item_id, item_data, db)


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete an item"""
    return await ItemService.delete(item_id, db)