from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import VendorTransactions, VendorMaster
from client_service.schemas.pydantic_schemas import TransactionCreate, TransactionUpdate
from client_service.api.constants.messages import TransactionMessages
from client_service.api.constants.status_codes import StatusCode
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class TransactionService:
    """Service class for Transaction business logic"""
    
    @staticmethod
    async def create(transaction_data: TransactionCreate, db: AsyncSession):
        """Create a new transaction"""
        try:
            # Check if InvoiceID already exists
            result = await db.execute(
                select(VendorTransactions).where(VendorTransactions.invoice_id == transaction_data.invoice_id)
            )
            existing_invoice = result.scalar_one_or_none()
            
            if existing_invoice:
                logger.warning(TransactionMessages.DUPLICATE_INVOICE.format(invoice=transaction_data.invoice_id))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=TransactionMessages.DUPLICATE_INVOICE.format(invoice=transaction_data.invoice_id)
                )

            # Verify VendorID exists
            result = await db.execute(
                select(VendorMaster).where(VendorMaster.vendor_id == transaction_data.vendor_id)
            )
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=TransactionMessages.VENDOR_NOT_FOUND.format(id=transaction_data.vendor_id)
                )

            # Create new transaction (UUID will be auto-generated)
            new_transaction = VendorTransactions(**transaction_data.model_dump(exclude_unset=True))
            
            db.add(new_transaction)
            await db.commit()
            await db.refresh(new_transaction)
            
            logger.info(TransactionMessages.CREATED_SUCCESS.format(invoice=new_transaction.invoice_id))
            return new_transaction

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(TransactionMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=TransactionMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(transaction_id: UUID, db: AsyncSession):
        """Get a transaction by ID"""
        try:
            result = await db.execute(
                select(VendorTransactions).where(VendorTransactions.transaction_id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=TransactionMessages.NOT_FOUND.format(id=transaction_id)
                )
            
            logger.info(TransactionMessages.RETRIEVED_SUCCESS.format(invoice=transaction.invoice_id))
            return transaction

        except HTTPException:
            raise
        except Exception as e:
            logger.error(TransactionMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=TransactionMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all transactions with pagination"""
        try:
            result = await db.execute(
                select(VendorTransactions).offset(skip).limit(limit)
            )
            transactions = result.scalars().all()
            
            logger.info(TransactionMessages.RETRIEVED_ALL_SUCCESS.format(count=len(transactions)))
            return list(transactions)

        except Exception as e:
            logger.error(TransactionMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=TransactionMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_vendor_id(vendor_id: UUID, db: AsyncSession):
        """Get all transactions by vendor ID"""
        try:
            result = await db.execute(
                select(VendorTransactions).where(VendorTransactions.vendor_id == vendor_id)
            )
            transactions = result.scalars().all()
            
            if not transactions:
                logger.info(TransactionMessages.NO_TRANSACTIONS_FOR_VENDOR.format(id=vendor_id))
                return []
            
            logger.info(TransactionMessages.RETRIEVED_BY_VENDOR_SUCCESS.format(count=len(transactions), id=vendor_id))
            return list(transactions)

        except Exception as e:
            logger.error(TransactionMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=TransactionMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(transaction_id: UUID, transaction_data: TransactionUpdate, db: AsyncSession):
        """Update a transaction"""
        try:
            result = await db.execute(
                select(VendorTransactions).where(VendorTransactions.transaction_id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=TransactionMessages.NOT_FOUND.format(id=transaction_id)
                )

            # Update fields
            for key, value in transaction_data.model_dump(exclude_unset=True).items():
                setattr(transaction, key, value)
            
            transaction.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(transaction)
            
            logger.info(TransactionMessages.UPDATED_SUCCESS.format(invoice=transaction.invoice_id))
            return transaction

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(TransactionMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=TransactionMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(transaction_id: UUID, db: AsyncSession):
        """Delete a transaction"""
        try:
            result = await db.execute(
                select(VendorTransactions).where(VendorTransactions.transaction_id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=TransactionMessages.NOT_FOUND.format(id=transaction_id)
                )

            await db.delete(transaction)
            await db.commit()
            
            logger.info(TransactionMessages.DELETED_SUCCESS.format(id=transaction_id))
            return {"message": TransactionMessages.DELETED_SUCCESS.format(id=transaction_id)}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(TransactionMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=TransactionMessages.DELETE_ERROR.format(error=str(e))
            )