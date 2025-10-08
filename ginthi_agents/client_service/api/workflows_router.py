from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.workflow_models import WorkflowRequestLedger
from client_service.schemas.client_db.client_models import Clients
from client_service.schemas.client_db.user_models import Users
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse
import logging
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/workflows/create", response_model=WorkflowResponse)
async def create_workflow_ledger(workflow_data: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if LedgerID already exists
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.LedgerID == workflow_data.LedgerID))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate workflow ledger creation attempt: LedgerID {workflow_data.LedgerID}")
            raise HTTPException(
                status_code=400,
                detail=f"Workflow ledger with LedgerID {workflow_data.LedgerID} already exists"
            )

        # Verify ClientID exists
        result = await db.execute(select(Clients).where(Clients.ClientID == workflow_data.ClientID))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {workflow_data.ClientID} not found"
            )

        # Verify UserID exists
        result = await db.execute(select(Users).where(Users.UserID == workflow_data.UserID))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {workflow_data.UserID} not found"
            )

        # Create new workflow
        new_workflow = WorkflowRequestLedger(**workflow_data.model_dump())
        
        db.add(new_workflow)
        await db.commit()
        await db.refresh(new_workflow)
        
        logger.info(f"Workflow ledger created successfully: {new_workflow.WorkflowName}")
        return new_workflow

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows/{ledger_id}", response_model=WorkflowResponse)
async def get_workflow_ledger(ledger_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.LedgerID == ledger_id))
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )
        
        logger.info(f"Workflow ledger retrieved: {workflow.WorkflowName}")
        return workflow

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows", response_model=list[WorkflowResponse])
async def get_all_workflow_ledgers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(WorkflowRequestLedger).offset(skip).limit(limit))
        workflows = result.scalars().all()
        
        logger.info(f"Retrieved {len(workflows)} workflow ledgers")
        return list(workflows)

    except Exception as e:
        logger.error(f"Error retrieving workflow ledgers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows/client/{client_id}", response_model=list[WorkflowResponse])
async def get_workflows_by_client(client_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.ClientID == client_id))
        workflows = result.scalars().all()
        
        if not workflows:
            logger.info(f"No workflow ledgers found for client {client_id}")
            return []
        
        logger.info(f"Retrieved {len(workflows)} workflow ledgers for client {client_id}")
        return list(workflows)

    except Exception as e:
        logger.error(f"Error retrieving client workflow ledgers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows/user/{user_id}", response_model=list[WorkflowResponse])
async def get_workflows_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.UserID == user_id))
        workflows = result.scalars().all()
        
        if not workflows:
            logger.info(f"No workflow ledgers found for user {user_id}")
            return []
        
        logger.info(f"Retrieved {len(workflows)} workflow ledgers for user {user_id}")
        return list(workflows)

    except Exception as e:
        logger.error(f"Error retrieving user workflow ledgers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/workflows/{ledger_id}", response_model=WorkflowResponse)
async def update_workflow_ledger(ledger_id: int, workflow_data: WorkflowUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.LedgerID == ledger_id))
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )

        # Update fields
        for key, value in workflow_data.model_dump(exclude_unset=True).items():
            setattr(workflow, key, value)
        
        workflow.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(workflow)
        
        logger.info(f"Workflow ledger updated: {workflow.WorkflowName}")
        return workflow

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/workflows/{ledger_id}/increment")
async def increment_workflow_request(ledger_id: int, db: AsyncSession = Depends(get_db)):
    """Increment the request count for a workflow"""
    try:
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.LedgerID == ledger_id))
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )

        # Increment count and update timestamp
        workflow.RequestCount += 1
        workflow.LastRequestAt = datetime.now(timezone.utc)
        workflow.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(workflow)
        
        logger.info(f"Workflow request count incremented: {workflow.WorkflowName}")
        
        return {
            "message": "Request count incremented",
            "workflow_name": workflow.WorkflowName,
            "request_count": workflow.RequestCount
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error incrementing workflow request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/workflows/{ledger_id}")
async def delete_workflow_ledger(ledger_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(WorkflowRequestLedger).where(WorkflowRequestLedger.LedgerID == ledger_id))
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )

        await db.delete(workflow)
        await db.commit()
        
        logger.info(f"Workflow ledger deleted: {workflow.WorkflowName}")
        return {"message": f"Workflow ledger {ledger_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")