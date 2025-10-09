from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.transactions_service import TransactionService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)
from uuid import UUID

router = APIRouter()


@router.post("/transactions/create", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new transaction"""
    return await TransactionService.create(transaction_data, db)


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a transaction by ID"""
    return await TransactionService.get_by_id(transaction_id, db)


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_all_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all transactions with pagination"""
    return await TransactionService.get_all(skip, limit, db)


@router.get("/transactions/vendor/{vendor_id}", response_model=list[TransactionResponse])
async def get_transactions_by_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all transactions by vendor ID"""
    return await TransactionService.get_by_vendor_id(vendor_id, db)


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a transaction"""
    return await TransactionService.update(transaction_id, transaction_data, db)


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a transaction"""
    return await TransactionService.delete(transaction_id, db)