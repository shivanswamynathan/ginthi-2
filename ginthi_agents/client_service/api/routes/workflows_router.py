from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.workflows_service import WorkflowService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse
)
from uuid import UUID

router = APIRouter()


@router.post("/workflows/create", response_model=WorkflowResponse)
async def create_workflow_ledger(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new workflow ledger"""
    return await WorkflowService.create(workflow_data, db)


@router.get("/workflows/{ledger_id}", response_model=WorkflowResponse)
async def get_workflow_ledger(
    ledger_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a workflow ledger by ID"""
    return await WorkflowService.get_by_id(ledger_id, db)


@router.get("/workflows", response_model=list[WorkflowResponse])
async def get_all_workflow_ledgers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all workflow ledgers with pagination"""
    return await WorkflowService.get_all(skip, limit, db)


@router.get("/workflows/client/{client_id}", response_model=list[WorkflowResponse])
async def get_workflows_by_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all workflow ledgers by client ID"""
    return await WorkflowService.get_by_client_id(client_id, db)


@router.get("/workflows/user/{user_id}", response_model=list[WorkflowResponse])
async def get_workflows_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all workflow ledgers by user ID"""
    return await WorkflowService.get_by_user_id(user_id, db)


@router.put("/workflows/{ledger_id}", response_model=WorkflowResponse)
async def update_workflow_ledger(
    ledger_id: UUID,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a workflow ledger"""
    return await WorkflowService.update(ledger_id, workflow_data, db)


@router.patch("/workflows/{ledger_id}/increment")
async def increment_workflow_request(
    ledger_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Increment the request count for a workflow ledger"""
    return await WorkflowService.increment(ledger_id, db)


@router.delete("/workflows/{ledger_id}")
async def delete_workflow_ledger(
    ledger_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a workflow ledger"""
    return await WorkflowService.delete(ledger_id, db)