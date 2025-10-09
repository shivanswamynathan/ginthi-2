from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.logs_service import LogService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    ActionLogCreate, ActionLogResponse,
    TransactionLogCreate, TransactionLogResponse,
    UserLogCreate, UserLogResponse
)
from uuid import UUID

router = APIRouter()


# ==================== ACTION LOG ROUTES ====================

@router.post("/action-logs/create", response_model=ActionLogResponse)
async def create_action_log(
    action_log_data: ActionLogCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new action log"""
    return await LogService.create_action_log(action_log_data, db)


@router.get("/action-logs/{log_id}", response_model=ActionLogResponse)
async def get_action_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get an action log by ID"""
    return await LogService.get_by_id_action_log(log_id, db)


@router.get("/action-logs", response_model=list[ActionLogResponse])
async def get_all_action_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all action logs with pagination"""
    return await LogService.get_all_action_logs(skip, limit, db)


# ==================== TRANSACTION LOG ROUTES ====================

@router.post("/transaction-logs/create", response_model=TransactionLogResponse)
async def create_transaction_log(
    transaction_log_data: TransactionLogCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new transaction log"""
    return await LogService.create_transaction_log(transaction_log_data, db)


@router.get("/transaction-logs/{log_id}", response_model=TransactionLogResponse)
async def get_transaction_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a transaction log by ID"""
    return await LogService.get_by_id_transaction_log(log_id, db)


@router.get("/transaction-logs/transaction/{transaction_id}", response_model=list[TransactionLogResponse])
async def get_logs_by_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all transaction logs by transaction ID"""
    return await LogService.get_by_transaction_id(transaction_id, db)


# ==================== USER LOG ROUTES ====================

@router.post("/user-logs/create", response_model=UserLogResponse)
async def create_user_log(
    user_log_data: UserLogCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new user log"""
    return await LogService.create_user_log(user_log_data, db)


@router.get("/user-logs/{log_id}", response_model=UserLogResponse)
async def get_user_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a user log by ID"""
    return await LogService.get_by_id_user_log(log_id, db)


@router.get("/user-logs/user/{user_id}", response_model=list[UserLogResponse])
async def get_logs_by_user(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all user logs by user ID with pagination"""
    return await LogService.get_by_user_id(user_id, skip, limit, db)


@router.get("/user-logs", response_model=list[UserLogResponse])
async def get_all_user_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all user logs with pagination"""
    return await LogService.get_all_user_logs(skip, limit, db)