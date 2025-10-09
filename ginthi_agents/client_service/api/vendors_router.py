from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import VendorMaster
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import VendorCreate, VendorUpdate, VendorResponse
import logging
from datetime import datetime, timezone
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/vendors/create", response_model=VendorResponse)
async def create_vendor(vendor_data: VendorCreate, db: AsyncSession = Depends(get_db)):
    try:
        
        # Check if VendorCode already exists
        result = await db.execute(select(VendorMaster).where(VendorMaster.VendorCode == vendor_data.VendorCode))
        existing_code = result.scalar_one_or_none()
        
        if existing_code:
            logger.warning(f"Duplicate vendor code: {vendor_data.VendorCode}")
            raise HTTPException(
                status_code=400,
                detail=f"Vendor with code '{vendor_data.VendorCode}' already exists"
            )

        # Create new vendor
        new_vendor = VendorMaster(**vendor_data.model_dump(exclude_unset=True))
        
        db.add(new_vendor)
        await db.commit()
        await db.refresh(new_vendor)
        
        logger.info(f"Vendor created successfully: {new_vendor.VendorName}")
        return new_vendor

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorMaster).where(VendorMaster.VendorID == vendor_id))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {vendor_id} not found"
            )
        
        logger.info(f"Vendor retrieved: {vendor.VendorName}")
        return vendor

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/vendors", response_model=list[VendorResponse])
async def get_all_vendors(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorMaster).offset(skip).limit(limit))
        vendors = result.scalars().all()
        
        logger.info(f"Retrieved {len(vendors)} vendors")
        return list(vendors)

    except Exception as e:
        logger.error(f"Error retrieving vendors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(vendor_id: UUID, vendor_data: VendorUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorMaster).where(VendorMaster.VendorID == vendor_id))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        # Update fields
        for key, value in vendor_data.model_dump(exclude_unset=True).items():
            setattr(vendor, key, value)
        
        vendor.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(vendor)
        
        logger.info(f"Vendor updated: {vendor.VendorName}")
        return vendor

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/vendors/{vendor_id}")
async def delete_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorMaster).where(VendorMaster.VendorID == vendor_id))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        await db.delete(vendor)
        await db.commit()
        
        logger.info(f"Vendor deleted: {vendor.VendorName}")
        return {"message": f"Vendor {vendor_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")