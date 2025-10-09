from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import VendorMaster
from client_service.schemas.pydantic_schemas import VendorCreate, VendorUpdate
from client_service.api.constants.messages import VendorMessages
from client_service.api.constants.status_codes import StatusCode
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class VendorService:
    """Service class for Vendor business logic"""
    
    @staticmethod
    async def create(vendor_data: VendorCreate, db: AsyncSession):
        """Create a new vendor"""
        try:
            # Check if VendorCode already exists
            result = await db.execute(
                select(VendorMaster).where(VendorMaster.vendor_code == vendor_data.vendor_code)
            )
            existing_code = result.scalar_one_or_none()
            
            if existing_code:
                logger.warning(VendorMessages.DUPLICATE_CODE.format(code=vendor_data.vendor_code))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=VendorMessages.DUPLICATE_CODE.format(code=vendor_data.vendor_code)
                )

            # Create new vendor (UUID will be auto-generated)
            new_vendor = VendorMaster(**vendor_data.model_dump(exclude_unset=True))
            
            db.add(new_vendor)
            await db.commit()
            await db.refresh(new_vendor)
            
            logger.info(VendorMessages.CREATED_SUCCESS.format(name=new_vendor.vendor_name))
            return new_vendor

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(VendorMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(vendor_id: UUID, db: AsyncSession):
        """Get a vendor by ID"""
        try:
            result = await db.execute(
                select(VendorMaster).where(VendorMaster.vendor_id == vendor_id)
            )
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorMessages.NOT_FOUND.format(id=vendor_id)
                )
            
            logger.info(VendorMessages.RETRIEVED_SUCCESS.format(name=vendor.vendor_name))
            return vendor

        except HTTPException:
            raise
        except Exception as e:
            logger.error(VendorMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all vendors with pagination"""
        try:
            result = await db.execute(
                select(VendorMaster).offset(skip).limit(limit)
            )
            vendors = result.scalars().all()
            
            logger.info(VendorMessages.RETRIEVED_ALL_SUCCESS.format(count=len(vendors)))
            return list(vendors)

        except Exception as e:
            logger.error(VendorMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(vendor_id: UUID, vendor_data: VendorUpdate, db: AsyncSession):
        """Update a vendor"""
        try:
            result = await db.execute(
                select(VendorMaster).where(VendorMaster.vendor_id == vendor_id)
            )
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorMessages.NOT_FOUND.format(id=vendor_id)
                )

            # Update fields
            for key, value in vendor_data.model_dump(exclude_unset=True).items():
                setattr(vendor, key, value)
            
            vendor.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(vendor)
            
            logger.info(VendorMessages.UPDATED_SUCCESS.format(name=vendor.vendor_name))
            return vendor

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(VendorMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(vendor_id: UUID, db: AsyncSession):
        """Delete a vendor"""
        try:
            result = await db.execute(
                select(VendorMaster).where(VendorMaster.vendor_id == vendor_id)
            )
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorMessages.NOT_FOUND.format(id=vendor_id)
                )

            await db.delete(vendor)
            await db.commit()
            
            logger.info(VendorMessages.DELETED_SUCCESS.format(id=vendor_id))
            return {"message": VendorMessages.DELETED_SUCCESS.format(id=vendor_id)}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(VendorMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorMessages.DELETE_ERROR.format(error=str(e))
            )