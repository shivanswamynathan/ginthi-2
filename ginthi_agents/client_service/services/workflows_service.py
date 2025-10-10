from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.workflow_models import WorkflowRequestLedger
from client_service.schemas.client_db.client_models import Clients
from client_service.schemas.client_db.user_models import Users
from client_service.schemas.pydantic_schemas import WorkflowCreate, WorkflowUpdate
from client_service.api.constants.messages import WorkflowMessages
from client_service.api.constants.status_codes import StatusCode
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service class for Workflow business logic"""
    
    @staticmethod
    async def create(workflow_data: WorkflowCreate, db: AsyncSession):
        """Create a new workflow ledger"""
        try:
            # Verify ClientID exists
            result = await db.execute(
                select(Clients).where(Clients.client_id == workflow_data.client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=WorkflowMessages.CLIENT_NOT_FOUND.format(id=workflow_data.client_id)
                )

            # Verify UserID exists
            result = await db.execute(
                select(Users).where(Users.user_id == workflow_data.user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=WorkflowMessages.USER_NOT_FOUND.format(id=workflow_data.user_id)
                )

            # Create new workflow (UUID will be auto-generated)
            new_workflow = WorkflowRequestLedger(**workflow_data.model_dump(exclude_unset=True))
            
            db.add(new_workflow)
            await db.commit()
            await db.refresh(new_workflow)
            
            logger.info(WorkflowMessages.CREATED_SUCCESS.format(name=new_workflow.workflow_name))
            return new_workflow

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(WorkflowMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(ledger_id: UUID, db: AsyncSession):
        """Get a workflow ledger by ID"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).where(WorkflowRequestLedger.ledger_id == ledger_id)
            )
            workflow = result.scalar_one_or_none()
            
            if not workflow:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=WorkflowMessages.NOT_FOUND.format(id=ledger_id)
                )
            
            logger.info(WorkflowMessages.RETRIEVED_SUCCESS.format(name=workflow.workflow_name))
            return workflow

        except HTTPException:
            raise
        except Exception as e:
            logger.error(WorkflowMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all workflow ledgers with pagination"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).offset(skip).limit(limit)
            )
            workflows = result.scalars().all()
            
            logger.info(WorkflowMessages.RETRIEVED_ALL_SUCCESS.format(count=len(workflows)))
            return list(workflows)

        except Exception as e:
            logger.error(WorkflowMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_client_id(client_id: UUID, db: AsyncSession):
        """Get all workflow ledgers by client ID"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).where(WorkflowRequestLedger.client_id == client_id)
            )
            workflows = result.scalars().all()
            
            if not workflows:
                logger.info(WorkflowMessages.NO_WORKFLOWS_FOR_CLIENT.format(id=client_id))
                return []
            
            logger.info(WorkflowMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(count=len(workflows), id=client_id))
            return list(workflows)

        except Exception as e:
            logger.error(WorkflowMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_user_id(user_id: UUID, db: AsyncSession):
        """Get all workflow ledgers by user ID"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).where(WorkflowRequestLedger.user_id == user_id)
            )
            workflows = result.scalars().all()
            
            if not workflows:
                logger.info(WorkflowMessages.NO_WORKFLOWS_FOR_USER.format(id=user_id))
                return []
            
            logger.info(WorkflowMessages.RETRIEVED_BY_USER_SUCCESS.format(count=len(workflows), id=user_id))
            return list(workflows)

        except Exception as e:
            logger.error(WorkflowMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(ledger_id: UUID, workflow_data: WorkflowUpdate, db: AsyncSession):
        """Update a workflow ledger"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).where(WorkflowRequestLedger.ledger_id == ledger_id)
            )
            workflow = result.scalar_one_or_none()
            
            if not workflow:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=WorkflowMessages.NOT_FOUND.format(id=ledger_id)
                )

            # Update fields
            for key, value in workflow_data.model_dump(exclude_unset=True).items():
                setattr(workflow, key, value)
            
            workflow.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(workflow)
            
            logger.info(WorkflowMessages.UPDATED_SUCCESS.format(name=workflow.workflow_name))
            return workflow

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(WorkflowMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def increment(ledger_id: UUID, db: AsyncSession):
        """Increment the request count for a workflow ledger"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).where(WorkflowRequestLedger.ledger_id == ledger_id)
            )
            workflow = result.scalar_one_or_none()
            
            if not workflow:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=WorkflowMessages.NOT_FOUND.format(id=ledger_id)
                )

            # Increment count and update timestamps
            workflow.request_count += 1
            workflow.last_request_at = datetime.now(timezone.utc)
            workflow.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(workflow)
            
            logger.info(WorkflowMessages.REQUEST_INCREMENTED)
            
            return {
                "message": WorkflowMessages.REQUEST_INCREMENTED,
                "workflow_name": workflow.workflow_name,
                "request_count": workflow.request_count
            }

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(WorkflowMessages.INCREMENT_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.INCREMENT_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(ledger_id: UUID, db: AsyncSession):
        """Delete a workflow ledger"""
        try:
            result = await db.execute(
                select(WorkflowRequestLedger).where(WorkflowRequestLedger.ledger_id == ledger_id)
            )
            workflow = result.scalar_one_or_none()
            
            if not workflow:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=WorkflowMessages.NOT_FOUND.format(id=ledger_id)
                )

            await db.delete(workflow)
            await db.commit()
            
            logger.info(WorkflowMessages.DELETED_SUCCESS.format(id=ledger_id))
            return {"message": WorkflowMessages.DELETED_SUCCESS.format(id=ledger_id)}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(WorkflowMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=WorkflowMessages.DELETE_ERROR.format(error=str(e))
            )