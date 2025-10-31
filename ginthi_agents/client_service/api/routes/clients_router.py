from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.clients_service import ClientService
from client_service.api.dependencies import get_database_session
from client_service.schemas.base_response import APIResponse
from client_service.schemas.pydantic_schemas import (
    ClientCreate,
    ClientUpdate
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/clients/create",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new client",
    description="Creates a new client organization. Use when: 'create client', 'add client', 'register client'.",
)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new client"""
    return await ClientService.create(client_data, db)


@router.get(
    "/clients/{client_id}",
    response_model=APIResponse,
    summary="Get client by ID",
    description="Retrieves client details by UUID. Use when: 'get client', 'show client details', 'find client'.",
)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a client by ID"""
    return await ClientService.get_by_id(client_id, db)


@router.get(
    "/clients",
    response_model=APIResponse,
    summary="List all clients",
    description="Get paginated list of all clients. Use when: 'list clients', 'show all clients', 'get clients'.",
)
async def get_all_clients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all clients with pagination"""
    return await ClientService.get_all(skip, limit, db)


@router.put(
    "/clients/{client_id}",
    response_model=APIResponse,
    summary="Update client information",
    description="Updates client name or API key. Use when: 'update client', 'modify client', 'change client details'.",
)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a client"""
    return await ClientService.update(client_id, client_data, db)


@router.delete(
    "/clients/{client_id}",
    response_model=APIResponse,
    summary="Delete client",
    description="Permanently deletes a client and all related data. Use when: 'delete client', 'remove client'.",
)
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a client"""
    return await ClientService.delete(client_id, db)