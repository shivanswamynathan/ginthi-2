from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.items_service import ItemService
from client_service.api.dependencies import get_database_session
from client_service.schemas.base_response import APIResponse
from client_service.schemas.pydantic_schemas import (
    ItemCreate,
    ItemUpdate
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/items/create",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
    description="Creates a new item in master. Use when: 'create item', 'add product', 'register SKU'.",
)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new item"""
    return await ItemService.create(item_data, db)


@router.get(
    "/items/{item_id}",
    response_model=APIResponse,
    summary="Get item by ID",
    description="Retrieves item by UUID. Use when: 'get item', 'show product', 'find SKU'.",
)
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get an item by ID"""
    return await ItemService.get_by_id(item_id, db)


@router.get(
    "/items",
    response_model=APIResponse,
    summary="List all items",
    description="Get all items with pagination. Use when: 'list items', 'show all products'.",
)
async def get_all_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all items with pagination"""
    return await ItemService.get_all(skip, limit, db)


@router.get(
    "/items/search/{item_code}",
    response_model=APIResponse,
    summary="Get item by code",
    description="Search item by code/SKU. Use when: 'search item by code', 'find product by SKU'.",
)
async def get_item_by_code(
    item_code: str,
    db: AsyncSession = Depends(get_database_session)
):
    """Get an item by code"""
    return await ItemService.get_by_code(item_code, db)


@router.put(
    "/items/{item_id}",
    response_model=APIResponse,
    summary="Update item",
    description="Updates item details. Use when: 'update item', 'modify product'.",
)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update an item"""
    return await ItemService.update(item_id, item_data, db)


@router.delete(
    "/items/{item_id}",
    response_model=APIResponse,
    summary="Delete item",
    description="Deletes an item. Use when: 'delete item', 'remove product'.",
)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete an item"""
    return await ItemService.delete(item_id, db)