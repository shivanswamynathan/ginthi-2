from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.workflow_models import WorkflowRequestLedger
from client_service.schemas.client_db.client_models import Clients
from client_service.schemas.client_db.user_models import Users
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== WORKFLOW REQUEST LEDGER CRUD ====================

@router.post("/workflows/create", response_model=WorkflowRequestLedger)
async def create_workflow_ledger(workflow: WorkflowRequestLedger, db=Depends(get_db)):
    try:
        # Check if LedgerID already exists
        existing = await WorkflowRequestLedger.find_one(
            WorkflowRequestLedger.LedgerID == workflow.LedgerID
        )
        if existing:
            logger.warning(f"Duplicate workflow ledger creation attempt: LedgerID {workflow.LedgerID}")
            raise HTTPException(
                status_code=400,
                detail=f"Workflow ledger with LedgerID {workflow.LedgerID} already exists"
            )

        # Verify ClientID exists
        client = await Clients.find_one(Clients.ClientID == workflow.ClientID)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {workflow.ClientID} not found"
            )

        # Verify UserID exists
        user = await Users.find_one(Users.UserID == workflow.UserID)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {workflow.UserID} not found"
            )

        # Insert the workflow ledger
        await workflow.insert()
        logger.info(f"Workflow ledger created successfully: {workflow.WorkflowName}")
        
        return workflow

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows/{ledger_id}", response_model=WorkflowRequestLedger)
async def get_workflow_ledger(ledger_id: int, db=Depends(get_db)):
    try:
        workflow = await WorkflowRequestLedger.find_one(
            WorkflowRequestLedger.LedgerID == ledger_id,
            fetch_links=True
        )
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


@router.get("/workflows", response_model=list[WorkflowRequestLedger])
async def get_all_workflow_ledgers(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        workflows = await WorkflowRequestLedger.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(workflows)} workflow ledgers")
        return workflows

    except Exception as e:
        logger.error(f"Error retrieving workflow ledgers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows/client/{client_id}", response_model=list[WorkflowRequestLedger])
async def get_workflows_by_client(client_id: int, db=Depends(get_db)):
    try:
        workflows = await WorkflowRequestLedger.find(
            WorkflowRequestLedger.ClientID == client_id
        ).to_list()
        
        if not workflows:
            logger.info(f"No workflow ledgers found for client {client_id}")
            return []
        
        logger.info(f"Retrieved {len(workflows)} workflow ledgers for client {client_id}")
        return workflows

    except Exception as e:
        logger.error(f"Error retrieving client workflow ledgers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/workflows/user/{user_id}", response_model=list[WorkflowRequestLedger])
async def get_workflows_by_user(user_id: int, db=Depends(get_db)):
    try:
        workflows = await WorkflowRequestLedger.find(
            WorkflowRequestLedger.UserID == user_id
        ).to_list()
        
        if not workflows:
            logger.info(f"No workflow ledgers found for user {user_id}")
            return []
        
        logger.info(f"Retrieved {len(workflows)} workflow ledgers for user {user_id}")
        return workflows

    except Exception as e:
        logger.error(f"Error retrieving user workflow ledgers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/workflows/{ledger_id}", response_model=WorkflowRequestLedger)
async def update_workflow_ledger(ledger_id: int, workflow_data: WorkflowRequestLedger, db=Depends(get_db)):
    try:
        workflow = await WorkflowRequestLedger.find_one(
            WorkflowRequestLedger.LedgerID == ledger_id
        )
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )

        # Update fields
        workflow.ClientID = workflow_data.ClientID
        workflow.UserID = workflow_data.UserID
        workflow.WorkflowName = workflow_data.WorkflowName
        workflow.RequestCount = workflow_data.RequestCount
        workflow.LastRequestAt = workflow_data.LastRequestAt
        workflow.UpdatedAt = datetime.now(timezone.utc)

        await workflow.save()
        logger.info(f"Workflow ledger updated: {workflow.WorkflowName}")
        
        return workflow

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/workflows/{ledger_id}/increment")
async def increment_workflow_request(ledger_id: int, db=Depends(get_db)):
    """Increment the request count for a workflow"""
    try:
        workflow = await WorkflowRequestLedger.find_one(
            WorkflowRequestLedger.LedgerID == ledger_id
        )
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )

        # Increment count and update timestamp
        workflow.RequestCount += 1
        workflow.LastRequestAt = datetime.now(timezone.utc)
        workflow.UpdatedAt = datetime.now(timezone.utc)

        await workflow.save()
        logger.info(f"Workflow request count incremented: {workflow.WorkflowName}")
        
        return {
            "message": "Request count incremented",
            "workflow_name": workflow.WorkflowName,
            "request_count": workflow.RequestCount
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error incrementing workflow request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/workflows/{ledger_id}")
async def delete_workflow_ledger(ledger_id: int, db=Depends(get_db)):
    try:
        workflow = await WorkflowRequestLedger.find_one(
            WorkflowRequestLedger.LedgerID == ledger_id
        )
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow ledger with ID {ledger_id} not found"
            )

        await workflow.delete()
        logger.info(f"Workflow ledger deleted: {workflow.WorkflowName}")
        
        return {"message": f"Workflow ledger {ledger_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow ledger: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
