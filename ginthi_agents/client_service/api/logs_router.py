from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import ActionLog, TransactionLog
from client_service.schemas.client_db.user_models import UserLog
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import (
    ActionLogCreate, ActionLogResponse,
    TransactionLogCreate, TransactionLogResponse,
    UserLogCreate, UserLogResponse
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== ACTION LOG CRUD ====================

@router.post("/action-logs/create", response_model=ActionLogResponse)
async def create_action_log(action_log_data: ActionLogCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if LogId already exists
        result = await db.execute(select(ActionLog).where(ActionLog.LogId == action_log_data.LogId))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate action log creation attempt: LogId {action_log_data.LogId}")
            raise HTTPException(
                status_code=400,
                detail=f"Action log with LogId {action_log_data.LogId} already exists"
            )

        # Create new action log
        new_action_log = ActionLog(**action_log_data.model_dump())
        
        db.add(new_action_log)
        await db.commit()
        await db.refresh(new_action_log)
        
        logger.info(f"Action log created successfully: LogId {new_action_log.LogId}")
        return new_action_log

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating action log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/action-logs/{log_id}", response_model=ActionLogResponse)
async def get_action_log(log_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ActionLog).where(ActionLog.LogId == log_id))
        action_log = result.scalar_one_or_none()
        
        if not action_log:
            raise HTTPException(
                status_code=404,
                detail=f"Action log with ID {log_id} not found"
            )
        
        logger.info(f"Action log retrieved: LogId {action_log.LogId}")
        return action_log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving action log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/action-logs", response_model=list[ActionLogResponse])
async def get_all_action_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ActionLog).offset(skip).limit(limit))
        action_logs = result.scalars().all()
        
        logger.info(f"Retrieved {len(action_logs)} action logs")
        return list(action_logs)

    except Exception as e:
        logger.error(f"Error retrieving action logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ==================== TRANSACTION LOG CRUD ====================

@router.post("/transaction-logs/create", response_model=TransactionLogResponse)
async def create_transaction_log(transaction_log_data: TransactionLogCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if LogID already exists
        result = await db.execute(select(TransactionLog).where(TransactionLog.LogID == transaction_log_data.LogID))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate transaction log creation attempt: LogID {transaction_log_data.LogID}")
            raise HTTPException(
                status_code=400,
                detail=f"Transaction log with LogID {transaction_log_data.LogID} already exists"
            )

        # Create new transaction log
        new_transaction_log = TransactionLog(**transaction_log_data.model_dump())
        
        db.add(new_transaction_log)
        await db.commit()
        await db.refresh(new_transaction_log)
        
        logger.info(f"Transaction log created successfully: LogID {new_transaction_log.LogID}")
        return new_transaction_log

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating transaction log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transaction-logs/{log_id}", response_model=TransactionLogResponse)
async def get_transaction_log(log_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TransactionLog).where(TransactionLog.LogID == log_id))
        transaction_log = result.scalar_one_or_none()
        
        if not transaction_log:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction log with ID {log_id} not found"
            )
        
        logger.info(f"Transaction log retrieved: LogID {transaction_log.LogID}")
        return transaction_log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transaction-logs/transaction/{transaction_id}", response_model=list[TransactionLogResponse])
async def get_logs_by_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TransactionLog).where(TransactionLog.TransactionID == transaction_id))
        transaction_logs = result.scalars().all()
        
        if not transaction_logs:
            logger.info(f"No logs found for transaction {transaction_id}")
            return []
        
        logger.info(f"Retrieved {len(transaction_logs)} logs for transaction {transaction_id}")
        return list(transaction_logs)

    except Exception as e:
        logger.error(f"Error retrieving transaction logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ==================== USER LOG CRUD ====================

@router.post("/user-logs/create", response_model=UserLogResponse)
async def create_user_log(user_log_data: UserLogCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if LogId already exists
        result = await db.execute(select(UserLog).where(UserLog.LogId == user_log_data.LogId))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate user log creation attempt: LogId {user_log_data.LogId}")
            raise HTTPException(
                status_code=400,
                detail=f"User log with LogId {user_log_data.LogId} already exists"
            )

        # Create new user log
        new_user_log = UserLog(**user_log_data.model_dump())
        
        db.add(new_user_log)
        await db.commit()
        await db.refresh(new_user_log)
        
        logger.info(f"User log created successfully: LogId {new_user_log.LogId}")
        return new_user_log

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-logs/{log_id}", response_model=UserLogResponse)
async def get_user_log(log_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(UserLog).where(UserLog.LogId == log_id))
        user_log = result.scalar_one_or_none()
        
        if not user_log:
            raise HTTPException(
                status_code=404,
                detail=f"User log with ID {log_id} not found"
            )
        
        logger.info(f"User log retrieved: LogId {user_log.LogId}")
        return user_log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-logs/user/{user_id}", response_model=list[UserLogResponse])
async def get_logs_by_user(user_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(UserLog)
            .where(UserLog.UserID == user_id)
            .offset(skip)
            .limit(limit)
        )
        user_logs = result.scalars().all()
        
        if not user_logs:
            logger.info(f"No logs found for user {user_id}")
            return []
        
        logger.info(f"Retrieved {len(user_logs)} logs for user {user_id}")
        return list(user_logs)

    except Exception as e:
        logger.error(f"Error retrieving user logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-logs", response_model=list[UserLogResponse])
async def get_all_user_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(UserLog).offset(skip).limit(limit))
        user_logs = result.scalars().all()
        
        logger.info(f"Retrieved {len(user_logs)} user logs")
        return list(user_logs)

    except Exception as e:
        logger.error(f"Error retrieving user logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")