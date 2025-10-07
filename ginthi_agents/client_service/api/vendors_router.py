from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.vendor_models import VendorMaster, VendorTransactions
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== VENDOR MASTER CRUD ====================


@router.post("/vendors/create", response_model=VendorMaster)
async def create_vendor(vendor: VendorMaster, db=Depends(get_db)):
    try:
        # Check if VendorID already exists
        existing = await VendorMaster.find_one(VendorMaster.VendorID == vendor.VendorID)
        if existing:
            logger.warning(f"Duplicate vendor creation attempt: VendorID {vendor.VendorID}")
            raise HTTPException(
                status_code=400,
                detail=f"Vendor with VendorID {vendor.VendorID} already exists"
            )

        # Check if VendorCode already exists
        existing_code = await VendorMaster.find_one(VendorMaster.VendorCode == vendor.VendorCode)
        if existing_code:
            logger.warning(f"Duplicate vendor code: {vendor.VendorCode}")
            raise HTTPException(
                status_code=400,
                detail=f"Vendor with code '{vendor.VendorCode}' already exists"
            )

        # Insert the vendor
        await vendor.insert()
        logger.info(f"Vendor created successfully: {vendor.VendorName}")
        
        return vendor

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/vendors/{vendor_id}", response_model=VendorMaster)
async def get_vendor(vendor_id: int, db=Depends(get_db)):
    try:
        vendor = await VendorMaster.find_one(VendorMaster.VendorID == vendor_id)
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


@router.get("/vendors", response_model=list[VendorMaster])
async def get_all_vendors(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        vendors = await VendorMaster.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(vendors)} vendors")
        return vendors

    except Exception as e:
        logger.error(f"Error retrieving vendors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/vendors/{vendor_id}", response_model=VendorMaster)
async def update_vendor(vendor_id: int, vendor_data: VendorMaster, db=Depends(get_db)):
    try:
        vendor = await VendorMaster.find_one(VendorMaster.VendorID == vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        # Update fields
        vendor.VendorName = vendor_data.VendorName
        vendor.VendorCode = vendor_data.VendorCode
        vendor.Email = vendor_data.Email
        vendor.GSTID = vendor_data.GSTID
        vendor.CompanyPan = vendor_data.CompanyPan
        vendor.BankAccNo = vendor_data.BankAccNo
        vendor.IfscCode = vendor_data.IfscCode
        vendor.UpdatedAt = datetime.utcnow()

        await vendor.save()
        logger.info(f"Vendor updated: {vendor.VendorName}")
        
        return vendor

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/vendors/{vendor_id}")
async def delete_vendor(vendor_id: int, db=Depends(get_db)):
    try:
        vendor = await VendorMaster.find_one(VendorMaster.VendorID == vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        await vendor.delete()
        logger.info(f"Vendor deleted: {vendor.VendorName}")
        
        return {"message": f"Vendor {vendor_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vendor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")