from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.vendors_service import VendorService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    VendorCreate,
    VendorUpdate,
    VendorResponse
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/vendors/create",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create vendor",
    description="Creates a new vendor/supplier. Use when: 'create vendor', 'add supplier', 'register vendor'.",
)
async def create_vendor(
    vendor_data: VendorCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new vendor"""
    return await VendorService.create(vendor_data, db)


@router.get(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor by ID",
    description="Retrieves vendor details by UUID. Use when: 'get vendor', 'show vendor', 'find supplier'.",
)
async def get_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a vendor by ID"""
    return await VendorService.get_by_id(vendor_id, db)


@router.get(
    "/vendors",
    response_model=list[VendorResponse],
    summary="List all vendors",
    description="Get all vendors with pagination. Use when: 'list vendors', 'show all suppliers'.",
)
async def get_all_vendors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all vendors with pagination"""
    return await VendorService.get_all(skip, limit, db)


@router.put(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Update vendor",
    description="Updates vendor information. Use when: 'update vendor', 'modify supplier details'.",
)
async def update_vendor(
    vendor_id: UUID,
    vendor_data: VendorUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a vendor"""
    return await VendorService.update(vendor_id, vendor_data, db)


@router.delete(
    "/vendors/{vendor_id}",
    summary="Delete vendor",
    description="Deletes a vendor permanently. Use when: 'delete vendor', 'remove supplier'.",
)
async def delete_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a vendor"""
    return await VendorService.delete(vendor_id, db)