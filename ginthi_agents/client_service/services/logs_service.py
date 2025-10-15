from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.vendor_models import ActionLog, TransactionLog
from client_service.schemas.client_db.user_models import UserLog
from client_service.schemas.pydantic_schemas import (
    ActionLogCreate, ActionLogResponse,
    TransactionLogCreate, TransactionLogResponse,
    UserLogCreate, UserLogResponse
)
from client_service.api.constants.messages import LogMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class LogService:
    """Service class for Log business logic"""
    
    # ==================== ACTION LOG METHODS ====================
    
    @staticmethod
    async def create_action_log(action_log_data: ActionLogCreate, db: AsyncSession):
        """Create a new action log"""
        try:
            # Create new action log (UUID will be auto-generated)
            new_action_log = ActionLog(**action_log_data.model_dump(exclude_unset=True))
            
            db.add(new_action_log)
            await db.commit()
            await db.refresh(new_action_log)
            
            logger.info(LogMessages.ACTION_LOG_CREATED.format(id=new_action_log.log_id))
            return APIResponse(
                success=True,
                message=LogMessages.ACTION_LOG_CREATED.format(id=new_action_log.log_id),
                data=ActionLogResponse.model_validate(new_action_log).model_dump()
            )

        except Exception as e:
            await db.rollback()
            logger.error(LogMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id_action_log(log_id: UUID, db: AsyncSession):
        """Get an action log by ID"""
        try:
            result = await db.execute(
                select(ActionLog).where(ActionLog.log_id == log_id)
            )
            action_log = result.scalar_one_or_none()
            
            if not action_log:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=LogMessages.LOG_NOT_FOUND.format(id=log_id)
                )
            
            logger.info(LogMessages.LOG_RETRIEVED.format(id=action_log.log_id))
            return APIResponse(
                success=True,
                message=LogMessages.LOG_RETRIEVED.format(id=action_log.log_id),
                data=ActionLogResponse.model_validate(action_log).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all_action_logs(skip: int, limit: int, db: AsyncSession):
        """Get all action logs with pagination"""
        try:
            result = await db.execute(
                select(ActionLog).offset(skip).limit(limit)
            )
            action_logs = result.scalars().all()
            
            logger.info(LogMessages.LOGS_RETRIEVED.format(count=len(action_logs)))
            return APIResponse(
                success=True,
                message=LogMessages.LOGS_RETRIEVED.format(count=len(action_logs)),
                data=[ActionLogResponse.model_validate(log).model_dump() for log in action_logs]
            )

        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    # ==================== TRANSACTION LOG METHODS ====================
    
    @staticmethod
    async def create_transaction_log(transaction_log_data: TransactionLogCreate, db: AsyncSession):
        """Create a new transaction log"""
        try:
            # Create new transaction log (UUID will be auto-generated)
            new_transaction_log = TransactionLog(**transaction_log_data.model_dump(exclude_unset=True))
            
            db.add(new_transaction_log)
            await db.commit()
            await db.refresh(new_transaction_log)
            
            logger.info(LogMessages.TRANSACTION_LOG_CREATED.format(id=new_transaction_log.log_id))
            return APIResponse(
                success=True,
                message=LogMessages.TRANSACTION_LOG_CREATED.format(id=new_transaction_log.log_id),
                data=TransactionLogResponse.model_validate(new_transaction_log).model_dump()
            )

        except Exception as e:
            await db.rollback()
            logger.error(LogMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id_transaction_log(log_id: UUID, db: AsyncSession):
        """Get a transaction log by ID"""
        try:
            result = await db.execute(
                select(TransactionLog).where(TransactionLog.log_id == log_id)
            )
            transaction_log = result.scalar_one_or_none()
            
            if not transaction_log:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=LogMessages.LOG_NOT_FOUND.format(id=log_id)
                )
            
            logger.info(LogMessages.LOG_RETRIEVED.format(id=transaction_log.log_id))
            return APIResponse(
                success=True,
                message=LogMessages.LOG_RETRIEVED.format(id=transaction_log.log_id),
                data=TransactionLogResponse.model_validate(transaction_log).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_transaction_id(transaction_id: UUID, db: AsyncSession):
        """Get all transaction logs by transaction ID"""
        try:
            result = await db.execute(
                select(TransactionLog).where(TransactionLog.transaction_id == transaction_id)
            )
            transaction_logs = result.scalars().all()
            
            if not transaction_logs:
                logger.info(LogMessages.NO_LOGS_FOR_TRANSACTION.format(id=transaction_id))
                return []
            
            logger.info(LogMessages.LOGS_BY_TRANSACTION_RETRIEVED.format(count=len(transaction_logs), id=transaction_id))
            return APIResponse(
                success=True,
                message=LogMessages.LOGS_BY_TRANSACTION_RETRIEVED.format(count=len(transaction_logs), id=transaction_id),
                data=[TransactionLogResponse.model_validate(log).model_dump() for log in transaction_logs]
            )

        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    # ==================== USER LOG METHODS ====================
    
    @staticmethod
    async def create_user_log(user_log_data: UserLogCreate, db: AsyncSession):
        """Create a new user log"""
        try:
            # Create new user log (UUID will be auto-generated)
            new_user_log = UserLog(**user_log_data.model_dump(exclude_unset=True))
            
            db.add(new_user_log)
            await db.commit()
            await db.refresh(new_user_log)
            
            logger.info(LogMessages.USER_LOG_CREATED.format(id=new_user_log.log_id))
            return APIResponse(
                success=True,
                message=LogMessages.USER_LOG_CREATED.format(id=new_user_log.log_id),
                data=UserLogResponse.model_validate(new_user_log).model_dump()
            )

        except Exception as e:
            await db.rollback()
            logger.error(LogMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id_user_log(log_id: UUID, db: AsyncSession):
        """Get a user log by ID"""
        try:
            result = await db.execute(
                select(UserLog).where(UserLog.log_id == log_id)
            )
            user_log = result.scalar_one_or_none()
            
            if not user_log:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=LogMessages.LOG_NOT_FOUND.format(id=log_id)
                )
            
            logger.info(LogMessages.LOG_RETRIEVED.format(id=user_log.log_id))
            return APIResponse(
                success=True,
                message=LogMessages.LOG_RETRIEVED.format(id=user_log.log_id),
                data=UserLogResponse.model_validate(user_log).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_user_id(user_id: UUID, skip: int, limit: int, db: AsyncSession):
        """Get all user logs by user ID with pagination"""
        try:
            result = await db.execute(
                select(UserLog)
                .where(UserLog.user_id == user_id)
                .offset(skip)
                .limit(limit)
            )
            user_logs = result.scalars().all()
            
            if not user_logs:
                logger.info(LogMessages.NO_LOGS_FOR_USER.format(id=user_id))
                return []
            
            logger.info(LogMessages.LOGS_BY_USER_RETRIEVED.format(count=len(user_logs), id=user_id))
            return APIResponse(
                success=True,
                message=LogMessages.LOGS_BY_USER_RETRIEVED.format(count=len(user_logs), id=user_id),
                data=[UserLogResponse.model_validate(log).model_dump() for log in user_logs]
            )

        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all_user_logs(skip: int, limit: int, db: AsyncSession):
        """Get all user logs with pagination"""
        try:
            result = await db.execute(
                select(UserLog).offset(skip).limit(limit)
            )
            user_logs = result.scalars().all()
            
            logger.info(LogMessages.LOGS_RETRIEVED.format(count=len(user_logs)))
            return APIResponse(
                success=True,
                message=LogMessages.LOGS_RETRIEVED.format(count=len(user_logs)),
                data=[UserLogResponse.model_validate(log).model_dump() for log in user_logs]
            )

        except Exception as e:
            logger.error(LogMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=LogMessages.RETRIEVE_ERROR.format(error=str(e))
            )