from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.vendor_models import ActionLog, TransactionLog
from client_service.schemas.client_db.user_models import UserLog
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== ACTION LOG CRUD ====================

@router.post("/action-logs/create", response_model=ActionLog)
async def create_action_log(action_log: ActionLog, db=Depends(get_db)):
    try:
        # Check if LogId already exists
        existing = await ActionLog.find_one(ActionLog.LogId == action_log.LogId)
        if existing:
            logger.warning(f"Duplicate action log creation attempt: LogId {action_log.LogId}")
            raise HTTPException(
                status_code=400,
                detail=f"Action log with LogId {action_log.LogId} already exists"
            )

        # Insert the action log
        await action_log.insert()
        logger.info(f"Action log created successfully: LogId {action_log.LogId}")
        
        return action_log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating action log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/action-logs/{log_id}", response_model=ActionLog)
async def get_action_log(log_id: int, db=Depends(get_db)):
    try:
        action_log = await ActionLog.find_one(ActionLog.LogId == log_id)
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


@router.get("/action-logs", response_model=list[ActionLog])
async def get_all_action_logs(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        action_logs = await ActionLog.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(action_logs)} action logs")
        return action_logs

    except Exception as e:
        logger.error(f"Error retrieving action logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ==================== TRANSACTION LOG CRUD ====================

@router.post("/transaction-logs/create", response_model=TransactionLog)
async def create_transaction_log(transaction_log: TransactionLog, db=Depends(get_db)):
    try:
        # Check if LogID already exists
        existing = await TransactionLog.find_one(
            TransactionLog.LogID == transaction_log.LogID
        )
        if existing:
            logger.warning(f"Duplicate transaction log creation attempt: LogID {transaction_log.LogID}")
            raise HTTPException(
                status_code=400,
                detail=f"Transaction log with LogID {transaction_log.LogID} already exists"
            )

        # Insert the transaction log
        await transaction_log.insert()
        logger.info(f"Transaction log created successfully: LogID {transaction_log.LogID}")
        
        return transaction_log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/transaction-logs/{log_id}", response_model=TransactionLog)
async def get_transaction_log(log_id: int, db=Depends(get_db)):
    try:
        transaction_log = await TransactionLog.find_one(
            TransactionLog.LogID == log_id,
            fetch_links=True
        )
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


@router.get("/transaction-logs/transaction/{transaction_id}", response_model=list[TransactionLog])
async def get_logs_by_transaction(transaction_id: int, db=Depends(get_db)):
    try:
        transaction_logs = await TransactionLog.find(
            TransactionLog.TransactionID == transaction_id
        ).to_list()
        
        if not transaction_logs:
            logger.info(f"No logs found for transaction {transaction_id}")
            return []
        
        logger.info(f"Retrieved {len(transaction_logs)} logs for transaction {transaction_id}")
        return transaction_logs

    except Exception as e:
        logger.error(f"Error retrieving transaction logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ==================== USER LOG CRUD ====================

@router.post("/user-logs/create", response_model=UserLog)
async def create_user_log(user_log: UserLog, db=Depends(get_db)):
    try:
        # Check if LogId already exists
        existing = await UserLog.find_one(UserLog.LogId == user_log.LogId)
        if existing:
            logger.warning(f"Duplicate user log creation attempt: LogId {user_log.LogId}")
            raise HTTPException(
                status_code=400,
                detail=f"User log with LogId {user_log.LogId} already exists"
            )

        # Insert the user log
        await user_log.insert()
        logger.info(f"User log created successfully: LogId {user_log.LogId}")
        
        return user_log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-logs/{log_id}", response_model=UserLog)
async def get_user_log(log_id: int, db=Depends(get_db)):
    try:
        user_log = await UserLog.find_one(
            UserLog.LogId == log_id,
            fetch_links=True
        )
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


@router.get("/user-logs/user/{user_id}", response_model=list[UserLog])
async def get_logs_by_user(user_id: int, skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        user_logs = await UserLog.find(
            UserLog.UserID == user_id
        ).skip(skip).limit(limit).to_list()
        
        if not user_logs:
            logger.info(f"No logs found for user {user_id}")
            return []
        
        logger.info(f"Retrieved {len(user_logs)} logs for user {user_id}")
        return user_logs

    except Exception as e:
        logger.error(f"Error retrieving user logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user-logs", response_model=list[UserLog])
async def get_all_user_logs(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        user_logs = await UserLog.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(user_logs)} user logs")
        return user_logs

    except Exception as e:
        logger.error(f"Error retrieving user logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

