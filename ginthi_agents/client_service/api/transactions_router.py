from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.vendor_models import VendorTransactions, VendorMaster
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime
from decimal import Decimal

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/transactions/create", response_model=VendorTransactions)
async def create_transaction(transaction: VendorTransactions, db=Depends(get_db)):
    try:
        # Check if TransactionID already exists
        existing = await VendorTransactions.find_one(
            VendorTransactions.TransactionID == transaction.TransactionID
        )
        if existing:
            logger.warning(f"Duplicate transaction creation attempt: TransactionID {transaction.TransactionID}")
            raise HTTPException(
                status_code=400,
                detail=f"Transaction with TransactionID {transaction.TransactionID} already exists"
            )

        # Check if InvoiceID already exists
        existing_invoice = await VendorTransactions.find_one(
            VendorTransactions.InvoiceID == transaction.InvoiceID
        )
        if existing_invoice:
            logger.warning(f"Duplicate invoice ID: {transaction.InvoiceID}")
            raise HTTPException(
                status_code=400,
                detail=f"Transaction with InvoiceID '{transaction.InvoiceID}' already exists"
            )

        # Verify VendorID exists
        vendor = await VendorMaster.find_one(VendorMaster.VendorID == transaction.VendorID)
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {transaction.VendorID} not found"
            )

        # Insert the transaction
        await transaction.insert()
        logger.info(f"Transaction created successfully: {transaction.InvoiceID}")
        
        return transaction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transactions/{transaction_id}", response_model=VendorTransactions)
async def get_transaction(transaction_id: int, db=Depends(get_db)):
    try:
        transaction = await VendorTransactions.find_one(
            VendorTransactions.TransactionID == transaction_id,
            fetch_links=True
        )
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


@router.get("/transactions", response_model=list[VendorTransactions])
async def get_all_transactions(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        transactions = await VendorTransactions.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(transactions)} transactions")
        return transactions

    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transactions/vendor/{vendor_id}", response_model=list[VendorTransactions])
async def get_transactions_by_vendor(vendor_id: int, db=Depends(get_db)):
    try:
        transactions = await VendorTransactions.find(
            VendorTransactions.VendorID == vendor_id
        ).to_list()
        
        if not transactions:
            logger.info(f"No transactions found for vendor {vendor_id}")
            return []
        
        logger.info(f"Retrieved {len(transactions)} transactions for vendor {vendor_id}")
        return transactions

    except Exception as e:
        logger.error(f"Error retrieving vendor transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/transactions/{transaction_id}", response_model=VendorTransactions)
async def update_transaction(transaction_id: int, transaction_data: VendorTransactions, db=Depends(get_db)):
    try:
        transaction = await VendorTransactions.find_one(
            VendorTransactions.TransactionID == transaction_id
        )
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )

        # Update fields
        transaction.VendorID = transaction_data.VendorID
        transaction.InvoiceID = transaction_data.InvoiceID
        transaction.ClientEntityID = transaction_data.ClientEntityID
        transaction.TransactionDate = transaction_data.TransactionDate
        transaction.TransactionType = transaction_data.TransactionType
        transaction.Amount = transaction_data.Amount
        transaction.Currency = transaction_data.Currency
        transaction.Description = transaction_data.Description
        transaction.Notes = transaction_data.Notes
        transaction.Status = transaction_data.Status
        transaction.UpdatedAt = datetime.utcnow()

        await transaction.save()
        logger.info(f"Transaction updated: {transaction.InvoiceID}")
        
        return transaction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, db=Depends(get_db)):
    try:
        transaction = await VendorTransactions.find_one(
            VendorTransactions.TransactionID == transaction_id
        )
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )

        await transaction.delete()
        logger.info(f"Transaction deleted: {transaction.InvoiceID}")
        
        return {"message": f"Transaction {transaction_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")