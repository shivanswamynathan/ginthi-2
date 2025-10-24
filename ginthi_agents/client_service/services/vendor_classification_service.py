from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import VendorClassification, VendorMaster
from client_service.schemas.client_db.client_models import ClientEntity
from client_service.schemas.client_db.expense_models import ExpenseMaster
from client_service.schemas.pydantic_schemas import VendorClassificationCreate, VendorClassificationUpdate, VendorClassificationResponse
from client_service.api.constants.messages import VendorClassificationMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class VendorClassificationService:
    """Service class for Vendor Classification business logic"""
    
    @staticmethod
    async def create(classification_data: VendorClassificationCreate, db: AsyncSession):
        """Create a new vendor classification"""
        try:
            # Validate ClientEntity exists
            entity_result = await db.execute(
                select(ClientEntity).where(ClientEntity.entity_id == classification_data.client_entity_id)
            )
            existing_entity = entity_result.scalar_one_or_none()
            if not existing_entity:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorClassificationMessages.CLIENT_ENTITY_NOT_FOUND.format(entity_id=classification_data.client_entity_id)
                )

            # Validate ExpenseCategory exists
            category_result = await db.execute(
                select(ExpenseMaster).where(ExpenseMaster.category_id == classification_data.expense_category_id)
            )
            existing_category = category_result.scalar_one_or_none()
            if not existing_category:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorClassificationMessages.CATEGORY_NOT_FOUND.format(category_id=classification_data.expense_category_id)
                )

            # Validate Vendor exists
            vendor_result = await db.execute(
                select(VendorMaster).where(VendorMaster.vendor_id == classification_data.vendor_id)
            )
            existing_vendor = vendor_result.scalar_one_or_none()
            if not existing_vendor:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorClassificationMessages.VENDOR_NOT_FOUND.format(vendor_id=classification_data.vendor_id)
                )

            # Check for duplicate classification
            dup_result = await db.execute(
                select(VendorClassification).where(
                    VendorClassification.client_entity_id == classification_data.client_entity_id,
                    VendorClassification.expense_category_id == classification_data.expense_category_id,
                    VendorClassification.vendor_id == classification_data.vendor_id
                )
            )
            if dup_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=VendorClassificationMessages.DUPLICATE_CLASSIFICATION
                )

            # Create new classification
            new_classification = VendorClassification(**classification_data.model_dump(exclude_unset=True))
            
            db.add(new_classification)
            await db.commit()
            await db.refresh(new_classification)
            
            logger.info(VendorClassificationMessages.CREATED_SUCCESS.format(
                vendor_name=existing_vendor.vendor_name,
                category_name=existing_category.category_name
            ))
            return APIResponse(
                success=True,
                message=VendorClassificationMessages.CREATED_SUCCESS.format(
                    vendor_name=existing_vendor.vendor_name,
                    category_name=existing_category.category_name
                ),
                data=VendorClassificationResponse.model_validate(new_classification).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(VendorClassificationMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorClassificationMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_keys(client_entity_id: UUID, expense_category_id: UUID, vendor_id: UUID, db: AsyncSession):
        """Get a vendor classification by composite keys"""
        try:
            result = await db.execute(
                select(VendorClassification).where(
                    VendorClassification.client_entity_id == client_entity_id,
                    VendorClassification.expense_category_id == expense_category_id,
                    VendorClassification.vendor_id == vendor_id
                )
            )
            classification = result.scalar_one_or_none()
            
            if not classification:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorClassificationMessages.NOT_FOUND.format(
                        entity_id=client_entity_id,
                        category_id=expense_category_id,
                        vendor_id=vendor_id
                    )
                )

            # Fetch names for message
            vendor_result = await db.execute(select(VendorMaster).where(VendorMaster.vendor_id == vendor_id))
            category_result = await db.execute(select(ExpenseMaster).where(ExpenseMaster.category_id == expense_category_id))
            vendor_name = vendor_result.scalar_one_or_none().vendor_name if vendor_result.scalar_one_or_none() else "Unknown"
            category_name = category_result.scalar_one_or_none().category_name if category_result.scalar_one_or_none() else "Unknown"
            
            logger.info(VendorClassificationMessages.RETRIEVED_SUCCESS.format(
                vendor_name=vendor_name,
                category_name=category_name
            ))
            return APIResponse(
                success=True,
                message=VendorClassificationMessages.RETRIEVED_SUCCESS.format(
                    vendor_name=vendor_name,
                    category_name=category_name
                ),
                data=VendorClassificationResponse.model_validate(classification).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(VendorClassificationMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorClassificationMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all vendor classifications with pagination"""
        try:
            result = await db.execute(
                select(VendorClassification).offset(skip).limit(limit)
            )
            classifications = result.scalars().all()
            
            logger.info(VendorClassificationMessages.RETRIEVED_ALL_SUCCESS.format(count=len(classifications)))
            return APIResponse(
                success=True,
                message=VendorClassificationMessages.RETRIEVED_ALL_SUCCESS.format(count=len(classifications)),
                data=[VendorClassificationResponse.model_validate(cl).model_dump() for cl in classifications]
            )

        except Exception as e:
            logger.error(VendorClassificationMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorClassificationMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(client_entity_id: UUID, expense_category_id: UUID, vendor_id: UUID, update_data: VendorClassificationUpdate, db: AsyncSession):
        """Update a vendor classification (limited fields, as junction)"""
        try:
            result = await db.execute(
                select(VendorClassification).where(
                    VendorClassification.client_entity_id == client_entity_id,
                    VendorClassification.expense_category_id == expense_category_id,
                    VendorClassification.vendor_id == vendor_id
                )
            )
            classification = result.scalar_one_or_none()
            
            if not classification:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorClassificationMessages.NOT_FOUND.format(
                        entity_id=client_entity_id,
                        category_id=expense_category_id,
                        vendor_id=vendor_id
                    )
                )

            # For junction, updates might reassign (e.g., change category/vendor), but validate new FKs if provided
            update_dict = update_data.model_dump(exclude_unset=True)
            if 'expense_category_id' in update_dict and update_dict['expense_category_id'] != expense_category_id:
                new_category_result = await db.execute(
                    select(ExpenseMaster).where(ExpenseMaster.category_id == update_dict['expense_category_id'])
                )
                if not new_category_result.scalar_one_or_none():
                    raise HTTPException(
                        status_code=StatusCode.NOT_FOUND,
                        detail=VendorClassificationMessages.CATEGORY_NOT_FOUND.format(category_id=update_dict['expense_category_id'])
                    )
                # Update key – but for simplicity, assume no key change; delete/recreate if needed
            if 'vendor_id' in update_dict and update_dict['vendor_id'] != vendor_id:
                new_vendor_result = await db.execute(
                    select(VendorMaster).where(VendorMaster.vendor_id == update_dict['vendor_id'])
                )
                if not new_vendor_result.scalar_one_or_none():
                    raise HTTPException(
                        status_code=StatusCode.NOT_FOUND,
                        detail=VendorClassificationMessages.VENDOR_NOT_FOUND.format(vendor_id=update_dict['vendor_id'])
                    )
                # Similar for entity

            # Since junction has no updatable fields beyond keys, this might be for future extensions
            # For now, log and return unchanged
            classification.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(classification)
            
            logger.info(VendorClassificationMessages.UPDATED_SUCCESS)
            return APIResponse(
                success=True,
                message=VendorClassificationMessages.UPDATED_SUCCESS,
                data=VendorClassificationResponse.model_validate(classification).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(VendorClassificationMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorClassificationMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(client_entity_id: UUID, expense_category_id: UUID, vendor_id: UUID, db: AsyncSession):
        """Delete a vendor classification"""
        try:
            result = await db.execute(
                select(VendorClassification).where(
                    VendorClassification.client_entity_id == client_entity_id,
                    VendorClassification.expense_category_id == expense_category_id,
                    VendorClassification.vendor_id == vendor_id
                )
            )
            classification = result.scalar_one_or_none()
            
            if not classification:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=VendorClassificationMessages.NOT_FOUND.format(
                        entity_id=client_entity_id,
                        category_id=expense_category_id,
                        vendor_id=vendor_id
                    )
                )

            await db.delete(classification)
            await db.commit()
            
            logger.info(VendorClassificationMessages.DELETED_SUCCESS.format(
                vendor_id=vendor_id,
                category_id=expense_category_id
            ))
            return APIResponse(
                success=True,
                message=VendorClassificationMessages.DELETED_SUCCESS.format(
                    vendor_id=vendor_id,
                    category_id=expense_category_id
                ),
                data=None
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(VendorClassificationMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=VendorClassificationMessages.DELETE_ERROR.format(error=str(e))
            )