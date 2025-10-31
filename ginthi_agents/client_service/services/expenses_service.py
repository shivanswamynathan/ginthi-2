from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.expense_models import ExpenseMaster
from client_service.schemas.pydantic_schemas import ExpenseCategoryCreate, ExpenseCategoryUpdate, ExpenseCategoryResponse
from client_service.api.constants.messages import ExpenseCategoryMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service class for Expense Category business logic"""
    
    @staticmethod
    async def create(category_data: ExpenseCategoryCreate, db: AsyncSession):
        """Create a new expense category"""
        try:
            # Check if CategoryName already exists
            result = await db.execute(
                select(ExpenseMaster).where(ExpenseMaster.category_name == category_data.category_name)
            )
            existing_category = result.scalar_one_or_none()
            
            if existing_category:
                logger.warning(ExpenseCategoryMessages.DUPLICATE_NAME.format(name=category_data.category_name))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=ExpenseCategoryMessages.DUPLICATE_NAME.format(name=category_data.category_name)
                )

            # Create new category (UUID auto-generated)
            new_category = ExpenseMaster(**category_data.model_dump(exclude_unset=True))
            
            db.add(new_category)
            await db.commit()
            await db.refresh(new_category)
            
            logger.info(ExpenseCategoryMessages.CREATED_SUCCESS.format(name=new_category.category_name))
            return APIResponse(
                success=True,
                message=ExpenseCategoryMessages.CREATED_SUCCESS.format(name=new_category.category_name),
                data=ExpenseCategoryResponse.model_validate(new_category).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(ExpenseCategoryMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ExpenseCategoryMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(category_id: UUID, db: AsyncSession):
        """Get an expense category by ID"""
        try:
            result = await db.execute(
                select(ExpenseMaster).where(ExpenseMaster.category_id == category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ExpenseCategoryMessages.NOT_FOUND.format(id=category_id)
                )
            
            logger.info(ExpenseCategoryMessages.RETRIEVED_SUCCESS.format(name=category.category_name))
            return APIResponse(
                success=True,
                message=ExpenseCategoryMessages.RETRIEVED_SUCCESS.format(name=category.category_name),
                data=ExpenseCategoryResponse.model_validate(category).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(ExpenseCategoryMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ExpenseCategoryMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all expense categories with pagination"""
        try:
            result = await db.execute(
                select(ExpenseMaster).offset(skip).limit(limit)
            )
            categories = result.scalars().all()
            
            logger.info(ExpenseCategoryMessages.RETRIEVED_ALL_SUCCESS.format(count=len(categories)))
            return APIResponse(
                success=True,
                message=ExpenseCategoryMessages.RETRIEVED_ALL_SUCCESS.format(count=len(categories)),
                data=[ExpenseCategoryResponse.model_validate(cat).model_dump() for cat in categories]
            )

        except Exception as e:
            logger.error(ExpenseCategoryMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ExpenseCategoryMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(category_id: UUID, category_data: ExpenseCategoryUpdate, db: AsyncSession):
        """Update an expense category"""
        try:
            result = await db.execute(
                select(ExpenseMaster).where(ExpenseMaster.category_id == category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ExpenseCategoryMessages.NOT_FOUND.format(id=category_id)
                )

            # Check duplicate name if updated
            update_data = category_data.model_dump(exclude_unset=True)
            if 'category_name' in update_data:
                name_result = await db.execute(
                    select(ExpenseMaster).where(
                        ExpenseMaster.category_name == update_data['category_name'],
                        ExpenseMaster.category_id != category_id
                    )
                )
                if name_result.scalar_one_or_none():
                    raise HTTPException(
                        status_code=StatusCode.CONFLICT,
                        detail=ExpenseCategoryMessages.DUPLICATE_NAME.format(name=update_data['category_name'])
                    )

            # Update fields
            for key, value in update_data.items():
                setattr(category, key, value)
            
            category.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(category)
            
            logger.info(ExpenseCategoryMessages.UPDATED_SUCCESS.format(name=category.category_name))
            return APIResponse(
                success=True,
                message=ExpenseCategoryMessages.UPDATED_SUCCESS.format(name=category.category_name),
                data=ExpenseCategoryResponse.model_validate(category).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(ExpenseCategoryMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ExpenseCategoryMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(category_id: UUID, db: AsyncSession):
        """Delete an expense category"""
        try:
            result = await db.execute(
                select(ExpenseMaster).where(ExpenseMaster.category_id == category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ExpenseCategoryMessages.NOT_FOUND.format(id=category_id)
                )

            await db.delete(category)
            await db.commit()
            
            logger.info(ExpenseCategoryMessages.DELETED_SUCCESS.format(id=category_id))
            return APIResponse(
                success=True,
                message=ExpenseCategoryMessages.DELETED_SUCCESS.format(id=category_id),
                data=None
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(ExpenseCategoryMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ExpenseCategoryMessages.DELETE_ERROR.format(error=str(e))
            )