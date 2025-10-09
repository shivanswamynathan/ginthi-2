from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import VendorTransactions, VendorMaster
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import TransactionCreate, TransactionUpdate, TransactionResponse
import logging
from datetime import datetime, timezone
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/transactions/create", response_model=TransactionResponse)
async def create_transaction(transaction_data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    try:
        
        # Check if InvoiceID already exists
        result = await db.execute(select(VendorTransactions).where(VendorTransactions.InvoiceID == transaction_data.InvoiceID))
        existing_invoice = result.scalar_one_or_none()
        
        if existing_invoice:
            logger.warning(f"Duplicate invoice ID: {transaction_data.InvoiceID}")
            raise HTTPException(
                status_code=400,
                detail=f"Transaction with InvoiceID '{transaction_data.InvoiceID}' already exists"
            )

        # Verify VendorID exists
        result = await db.execute(select(VendorMaster).where(VendorMaster.VendorID == transaction_data.VendorID))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {transaction_data.VendorID} not found"
            )

        # Create new transaction
        new_transaction = VendorTransactions(**transaction_data.model_dump(exclude_unset=True))
        
        db.add(new_transaction)
        await db.commit()
        await db.refresh(new_transaction)
        
        logger.info(f"Transaction created successfully: {new_transaction.InvoiceID}")
        return new_transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorTransactions).where(VendorTransactions.TransactionID == transaction_id))
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )
        
        logger.info(f"Transaction retrieved: {transaction.InvoiceID}")
        return transaction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_all_transactions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorTransactions).offset(skip).limit(limit))
        transactions = result.scalars().all()
        
        logger.info(f"Retrieved {len(transactions)} transactions")
        return list(transactions)

    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transactions/vendor/{vendor_id}", response_model=list[TransactionResponse])
async def get_transactions_by_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorTransactions).where(VendorTransactions.VendorID == vendor_id))
        transactions = result.scalars().all()
        
        if not transactions:
            logger.info(f"No transactions found for vendor {vendor_id}")
            return []
        
        logger.info(f"Retrieved {len(transactions)} transactions for vendor {vendor_id}")
        return list(transactions)

    except Exception as e:
        logger.error(f"Error retrieving vendor transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: UUID, transaction_data: TransactionUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorTransactions).where(VendorTransactions.TransactionID == transaction_id))
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )

        # Update fields
        for key, value in transaction_data.model_dump(exclude_unset=True).items():
            setattr(transaction, key, value)
        
        transaction.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(transaction)
        
        logger.info(f"Transaction updated: {transaction.InvoiceID}")
        return transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(VendorTransactions).where(VendorTransactions.TransactionID == transaction_id))
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )

        await db.delete(transaction)
        await db.commit()
        
        logger.info(f"Transaction deleted: {transaction.InvoiceID}")
        return {"message": f"Transaction {transaction_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")